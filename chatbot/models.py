# chatbot/models.py
from django.db import models

class ProvisionRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]
    user_message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    terraform_output = models.TextField(null=True, blank=True) # We'll keep this for error logs
    created_at = models.DateTimeField(auto_now_add=True)

    # --- ADD THESE NEW FIELDS ---
    vm_name = models.CharField(max_length=100, null=True, blank=True)
    cpu = models.IntegerField(null=True, blank=True)
    memory = models.IntegerField(null=True, blank=True)
    ip_address = models.CharField(max_length=100, null=True, blank=True)
    # --------------------------

    def __str__(self):
        return f"Request ({self.id}) - {self.status}"