import subprocess
import os
import json
from celery import shared_task
from .models import ProvisionRequest
from django.conf import settings

# Use the absolute BASE_DIR from Django settings for a robust path
TERRAFORM_DIR = os.path.join(settings.BASE_DIR, 'terraform/vsphere_vm')

@shared_task
def run_terraform_provision(request_id, vm_params):
    """
    The main Celery task to provision a VM using Terraform.
    """
    req = ProvisionRequest.objects.get(id=request_id)
    req.status = 'RUNNING'
    req.save()

    # The vm_name will also be our unique workspace name for state isolation
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
        # --- Workspace Management ---
        # This ensures each VM has its own state file and they don't conflict.
        print(f"DEBUG: Ensuring workspace '{vm_name}' exists...")
        # First, try to create the new workspace. This fails harmlessly if it exists.
        subprocess.run(
            ["terraform", "workspace", "new", vm_name],
            cwd=TERRAFORM_DIR, capture_output=True, text=True
        )
        # Then, select it to make sure we're operating in the correct context.
        subprocess.run(
            ["terraform", "workspace", "select", vm_name],
            cwd=TERRAFORM_DIR, check=True, capture_output=True, text=True
        )
        # ---------------------------

        # --- Run Terraform ---
        print("DEBUG: Running 'terraform init'...")
        subprocess.run(["terraform", "init", "-upgrade"], cwd=TERRAFORM_DIR, check=True, capture_output=True, text=True)
        
        print("DEBUG: Running 'terraform apply'...")
        subprocess.run(["terraform", "apply", "-auto-approve"], cwd=TERRAFORM_DIR, check=True, capture_output=True, text=True)

        # --- Parse Success Output ---
        print("DEBUG: Getting outputs as JSON...")
        output_result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=TERRAFORM_DIR, check=True, capture_output=True, text=True
        )
        output_data = json.loads(output_result.stdout)
        ip_addr = output_data.get('ip_address', {}).get('value', 'Not Available')
        
        # --- Save Clean Data on Success ---
        req.status = 'SUCCESS'
        req.vm_name = vm_name
        req.cpu = vm_params.get('cpu')
        req.memory = vm_params.get('memory_gb')
        req.ip_address = ip_addr
        req.terraform_output = "Successfully provisioned."
        req.save()
        print(f"--- Terraform Task {request_id} Successful ---")

    except subprocess.CalledProcessError as e:
        # --- Handle and Parse Errors ---
        req.status = 'FAILED'
        error_log = e.stderr.lower() # Check the standard error output
        
        user_friendly_error = None
        if "insufficient capacity" in error_log or "out of resources" in error_log:
            user_friendly_error = "VM creation failed: The vSphere cluster has insufficient resources (CPU, Memory, or Storage). Please contact your administrator."
        elif "privilege required" in error_log:
            user_friendly_error = "VM creation failed due to a permissions error in vSphere. Please ensure the service account has the required privileges."
        elif "not found" in error_log:
             user_friendly_error = f"VM creation failed: A required resource was not found. It could be the template, network, or datastore. Details:\n{e.stderr}"

        if user_friendly_error:
            req.terraform_output = user_friendly_error
        else:
            # If it's an unknown error, save the full log for debugging
            req.terraform_output = f"An unexpected error occurred.\n\nDetails:\n{e.stderr}"
        
        req.save()
        print(f"--- Terraform Task {request_id} FAILED ---")
    
    finally:
        # --- Cleanup ---
        # Switch back to the default workspace to keep things tidy for manual runs.
        subprocess.run(["terraform", "workspace", "select", "default"], cwd=TERRAFORM_DIR, capture_output=True, text=True)
        # Clean up the generated tfvars file.
        if os.path.exists(tfvars_path):
            os.remove(tfvars_path)
    
    return req.status