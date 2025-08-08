import subprocess
import os
import re # <-- Import the regex module
from celery import shared_task
from .models import ProvisionRequest
from django.conf import settings

TERRAFORM_DIR = os.path.join(settings.BASE_DIR, 'terraform/vsphere_vm')

@shared_task
def run_terraform_provision(request_id, vm_params):
    req = ProvisionRequest.objects.get(id=request_id)
    req.status = 'RUNNING'
    req.save()

    # The vm_name will also be our unique workspace name
    vm_name = f"vm-bot-{request_id}"
    
    tfvars_content = f"""
    vm_name      = "{vm_name}"
    num_vcpus    = {vm_params.get('cpu')}
    memory_gb    = {vm_params.get('memory_gb')}
    image_name   = "{vm_params.get('image')}"
    """
    
    tfvars_path = os.path.join(TERRAFORM_DIR, 'chatbot.auto.tfvars')
    with open(tfvars_path, 'w') as f:
        f.write(tfvars_content)
    
    try:
        # --- NEW WORKSPACE LOGIC ---
        print(f"DEBUG: Ensuring workspace '{vm_name}' exists...")
        # Use a more robust way to run commands that might fail
        subprocess.run(
            ["terraform", "workspace", "select", vm_name], 
            cwd=TERRAFORM_DIR, capture_output=True, text=True
        )
        # The above command fails if the workspace doesn't exist, which is ok.
        # Now create it if it doesn't. `new` also selects it.
        subprocess.run(
            ["terraform", "workspace", "new", vm_name],
            cwd=TERRAFORM_DIR, capture_output=True, text=True
        )
        # ---------------------------

        print("DEBUG: Running 'terraform init'...")
        subprocess.run(["terraform", "init", "-upgrade"], cwd=TERRAFORM_DIR, check=True, capture_output=True, text=True)
        
        print("DEBUG: Running 'terraform apply'...")
        result = subprocess.run(["terraform", "apply", "-auto-approve"], cwd=TERRAFORM_DIR, check=True, capture_output=True, text=True)

        req.status = 'SUCCESS'
        req.terraform_output = result.stdout
        print(f"--- Terraform Task {request_id} Successful ---")

    except subprocess.CalledProcessError as e:
        req.status = 'FAILED'
        req.terraform_output = f"STDOUT:\n{e.stdout}\n\nSTDERR:\n{e.stderr}"
        print(f"--- Terraform Task {request_id} FAILED ---")
        print(req.terraform_output)
    finally:
        # Switch back to the default workspace to keep things clean
        subprocess.run(["terraform", "workspace", "select", "default"], cwd=TERRAFORM_DIR)
        req.save()
        if os.path.exists(tfvars_path):
            os.remove(tfvars_path)
    
    return req.status