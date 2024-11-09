# from .serializers import EncodeSerializers
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.response import Response

# Heartbeat request
def Heartbeat(request):
    return JsonResponse({'status': 'Backend is active'})

class Devfolio(APIView):
    def post(self, request, *args, **kwargs):
        projectURL = request.data.get('projectURL')
        return Response({'status': 'success'}, status=200)