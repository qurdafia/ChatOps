import subprocess
import os
import json
from celery import shared_task
from .models import ProvisionRequest
from django.conf import settings

TERRAFORM_DIR = os.path.join(settings.BASE_DIR, 'terraform/vsphere_vm')

@shared_task
def run_terraform_provision(request_id, vm_params):
    req = ProvisionRequest.objects.get(id=request_id)
    req.status = 'RUNNING'
    req.save()

    vm_name = f"vm-bot-{request_id}"
    
    tfvars_path = os.path.join(TERRAFORM_DIR, 'chatbot.auto.tfvars')
    tfvars_content = f"""
    vm_name      = "{vm_name}"
    num_vcpus    = {vm_params.get('cpu')}
    memory_gb    = {vm_params.get('memory_gb')}
    image_name   = "{vm_params.get('image')}"
    """
    with open(tfvars_path, 'w') as f:
        f.write(tfvars_content)

    try:
        # Run Terraform commands as before
        subprocess.run(["terraform", "init", "-upgrade"], cwd=TERRAFORM_DIR, check=True, capture_output=True, text=True)
        subprocess.run(["terraform", "apply", "-auto-approve"], cwd=TERRAFORM_DIR, check=True, capture_output=True, text=True)

        # Get the output as clean JSON
        output_result = subprocess.run(["terraform", "output", "-json"], cwd=TERRAFORM_DIR, check=True, capture_output=True, text=True)
        output_data = json.loads(output_result.stdout)
        ip_addr = output_data.get('ip_address', {}).get('value', 'N/A')

        # --- THE FIX IS HERE ---
        # Assign all the success data to the request object
        req.status = 'SUCCESS'
        req.vm_name = vm_name
        req.cpu = vm_params.get('cpu')
        req.memory = vm_params.get('memory_gb')
        req.ip_address = ip_addr
        req.terraform_output = "Successfully provisioned."
        
        # Save the successful result with all details to the database IMMEDIATELY
        req.save()
        # ---------------------

    except subprocess.CalledProcessError as e:
        req.status = 'FAILED'
        req.terraform_output = f"STDOUT:\n{e.stdout}\n\nSTDERR:\n{e.stderr}"
        # Save the failed result to the database
        req.save()
        
    finally:
        # The finally block is now only responsible for cleanup
        if os.path.exists(tfvars_path):
            os.remove(tfvars_path)
    
    return req.status