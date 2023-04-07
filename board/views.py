import traceback
from django.forms import ValidationError
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions, status
from rest_framework.response import Response

from board.permissions import IsBoardgroupMember
from .serializers import BoardSerializer, UserSerializer, TaskSerializer, CategorySerializer
from .models import Board, Task, Category
from django.core import serializers
from django.http import HttpResponse
from datetime import datetime
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

# Create your views here.
class BoardViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        ##user_id = self.kwargs.get('id', None)
        usertoken = self.request.META.get('HTTP_AUTHORIZATION')
        token = usertoken.split(' ')[1]
        token = Token.objects.get(key=token)
        user = token.user
        try:
            queryset = Board.objects.filter(board_users__id=user.id)
            return queryset
        except IndexError as e:
            return []
    

class CreateBoardViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'patch']
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    
    def get_group(self, board_users_list):
        numberOfGroups = Group.objects.filter(name__contains='boardgroup').count()
        newGroup = Group.objects.get_or_create(name=f"boardgroup{numberOfGroups}")
        newGroup = newGroup[0]
        newGroup.user_set.set(board_users_list)
        return newGroup
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        board_users_raw = request.data.get('board_users', None)
        board_users_list = User.objects.filter(id__in=board_users_raw)
        name=request.data.get("name", None)
        board = Board.objects.create(
            name=name,
            group=self.get_group(board_users_list)
        )
        for user in board_users_list:
            board.board_users.add(user)
        serialzed_board = serializers.serialize('json',[board])
        return HttpResponse(serialzed_board, status=status.HTTP_201_CREATED,content_type='application/json')
    
class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    authentication_classes = [TokenAuthentication]
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
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsBoardgroupMember]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def create(self, request, id=None):
        board = Board.objects.get(id=id)
        request_data = request.data.copy()
        request_data['board'] = board.id
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    def get_queryset(self):
        id = self.kwargs.get('id', None)
        if id:
            board = Board.objects.get(id=id)
            queryset = self.queryset.filter(board=board)
            return queryset
        return self.queryset
    
class TaskViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsBoardgroupMember]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    
    def get_category(self, request):
        category = request.data.get("category", None)
        category = Category.objects.get(id=category)
        return category
    
    def get_board(self):
        id = self.kwargs.get("id", None)
        board = Board.objects.get(id=id)
        return board
    
    def get_due_date(self, request):
        due_date = request.data.get("due_date", None)
        due_date = datetime.strptime(due_date, '%Y-%m-%d')
        return due_date
    
    def get_queryset(self):
        id = self.kwargs.get('id', None)
        if id:
            queryset = self.queryset.filter(board__id=id)
            return queryset
        return self.queryset
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

        
    
    def create(self, request, **kwargs):
        assigned_usersRaw = request.data.get("assigned_users", [])
        assigned_usersList = User.objects.filter(id__in=assigned_usersRaw)
        task = Task.objects.create(priority= request.data.get("priority", None),
                                   title = request.data.get("title", None), 
                                   description= request.data.get("description", None),
                                   due_date=self.get_due_date(request),
                                   status=request.data.get("status", None),
                                   board=self.get_board(),
                                   category=self.get_category(request))
        task.assigned_users.set(assigned_usersList)
        serialzed_task = serializers.serialize('json',[task])
        return HttpResponse(serialzed_task, status=status.HTTP_201_CREATED,content_type='application/json')
    
    