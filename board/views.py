from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework.response import Response
from board.permissions import IsBoardgroupMember
from .serializers import BoardSerializer, UserSerializer, TaskSerializer, CategorySerializer
from .models import Board, Task, Category
from django.core import serializers
from django.http import Http404, HttpResponse
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
# Create your views here.
class BoardViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch']
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Board.objects.filter(board_users__id=self.request.user.id)
        return queryset    
    
class UserView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_queryset(self):
        id = self.kwargs.get('id', None)
        if id:
            board = Board.objects.get(id=id)
            queryset = board.board_users
            return queryset
        return User.objects.all()
    
class CategoryViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated, IsBoardgroupMember]
    serializer_class = CategorySerializer
    
    def perform_create(self, serializer):
        id = self.kwargs.get('id', None)
        board = get_object_or_404(Board, id=id)
        serializer.save(board=board)
        
    def get_queryset(self):
        try:
            id = self.kwargs.get('id', None)
            board = Board.objects.get(id=id)
            queryset = Category.objects.filter(board=board)
            return queryset
        except:
            raise Http404
    
class TaskViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthenticated, IsBoardgroupMember]
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        try:
            id = self.kwargs.get('id', None)
            queryset = Task.objects.filter(board__id=id)
            return queryset
        except:
            raise Http404
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['board_id'] = self.kwargs.get('id')
        return context
    