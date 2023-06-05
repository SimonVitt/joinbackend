from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .serializers import ChangePasswordSerializer, CreateUserSerializer

import json

class LoginView(ObtainAuthToken):
    authentication_classes = []
    http_method_names = ['post']
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'username': user.username
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Wrong credentials"}, status=status.HTTP_400_BAD_REQUEST)
        
        
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            Token.objects.get(key=request.auth.key).delete()
        except Token.DoesNotExist:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
    
class CreateUserView(generics.CreateAPIView):
    authentication_classes = []
    serializer_class = CreateUserSerializer

class ChangePasswordView(generics.UpdateAPIView):
    http_method_names = ['patch']
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user           
            

@csrf_exempt  
def send_mail_view(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            email = body.get('email', None)
            user = User.objects.get(email=email)
            token, created = Token.objects.get_or_create(user=user)
            send_mail(
                'Rest Password',
                f'Hello {user.username}, \n please click on the Link to reset your password :) \n http://localhost:4200/resetpassword/{token}',
                'kontakt@simon-vitt.de',
                [email],
                fail_silently=False
            )
            return JsonResponse({"detail": "Email send."},status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return JsonResponse({"detail": "Email not found."}, status=status.HTTP_404_NOT_FOUND)
    