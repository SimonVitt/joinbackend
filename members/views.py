from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import viewsets, status, generics
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from .serializers import ChangePasswordSerializer
import json

class LoginView(ObtainAuthToken):
    http_method_names = ['post']
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })
        
class LogoutView(viewsets.views.APIView):
    authentication_classes = [TokenAuthentication]
    http_method_names = ['get']
    def get(self, request, format=None):
        usertoken = self.request.META.get('HTTP_AUTHORIZATION')
        try:
            token = usertoken.split(' ')[1]
            token = Token.objects.get(key=token).delete()
        except AttributeError as a:
            print(a)
        return Response(status=status.HTTP_200_OK)
    
class CreateUserView(viewsets.views.APIView):
    http_method_names = ['post']
    
    def post(self, request, * args, **kwargs):
        username = request.data.get('username', None)
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        
        usertest = User.objects.filter(username=username)
        emailtest = User.objects.filter(email=email)
        if(len(usertest) == 0 and len(emailtest) == 0):
            User.objects.create_user(username=username, email=email, password=password)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChangePasswordView(generics.UpdateAPIView):
    http_method_names = ['patch']
    model = User
    authentication_classes = [TokenAuthentication]
    serializer_class = ChangePasswordSerializer
    
    def partial_update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            user.set_password(request.data.get('password1', None))
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
            

@csrf_exempt  
def send_mail_view(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            email = body.get('email', None)
            print(email)
            user = User.objects.get(email=email)
            token, created = Token.objects.get_or_create(user=user)
            send_mail(
                'Rest Password',
                f'Hello {user.username}, \n please click on the Link to reset the yourpassword :) \n https://join.simon-vitt.de/resetpassword/{token}',
                'kontakt@simon-vitt.de',
                [email],
                fail_silently=False
            )
            return HttpResponse(status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    