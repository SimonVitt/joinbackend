from django.contrib import admin
from django.urls import include, path
from members.views import LoginView, LogoutView, CreateUserView, send_mail_view, ChangePasswordView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('signup/', CreateUserView.as_view()),
    path('sendemail/', send_mail_view),
    path('changepassword/', ChangePasswordView.as_view())
]