from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ProvisionRequest
from .tasks import run_terraform_provision
from .nlp import parse_provision_request

class ChatbotView(APIView):
    def post(self, request, *args, **kwargs):
        user_message = request.data.get('message')
        if not user_message:
            return Response({'error': 'Message not provided'}, status=status.HTTP_400_BAD_REQUEST)

        # --- NEW: Check for parsing errors ---
        vm_params, error_message = parse_provision_request(user_message)

        if error_message:
            # If the parser returned an error, send it to the user and stop.
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
        # ------------------------------------

        # If no error, proceed as before
        req = ProvisionRequest.objects.create(user_message=user_message, cpu=vm_params['cpu'], memory=vm_params['memory_gb'])
        run_terraform_provision.delay(req.id, vm_params)
        
        return Response(
            {'message': 'Request received. Processing...', 'request_id': req.id},
            status=status.HTTP_202_ACCEPTED
        )

class RequestStatusView(APIView):
    """
    Allows the frontend to poll for the status of a specific request.
    """
    def get(self, request, request_id, *args, **kwargs):
        try:
            req = ProvisionRequest.objects.get(id=request_id)
            # --- UPDATED to return the new fields ---
            return Response({
                'status': req.status,
                'output': req.terraform_output, # Will be a clean message or an error log
                'vm_details': {
                    'name': req.vm_name,
                    'cpu': req.cpu,
                    'memory': req.memory,
                    'ip_address': req.ip_address,
                }
            })
            # ------------------------------------
        except ProvisionRequest.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)