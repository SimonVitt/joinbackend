from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Board, Task, Category

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'id', 'email']
        
    def to_internal_value(self, data):
        if isinstance(data, int):
            user = User.objects.get(pk=data)
            return user
        else:
            return super().to_internal_value(data)
        
class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['name']
        
class BoardSerializer(serializers.HyperlinkedModelSerializer):
    board_users = UserSerializer(many=True)
    group = GroupSerializer(required=False)
    class Meta:
        model = Board
        fields = ['name', 'group', 'board_users', 'id']
        
    def update(self, instance, validated_data):
        new_board_users = validated_data.pop("board_users", None)
        if new_board_users:
            instance.group.user_set.set(new_board_users)
            instance.board_users.set(new_board_users)
        return super().update(instance, validated_data)
    
    def create_group(self, board_users_list):
        numberOfGroups = Group.objects.filter(name__contains='boardgroup').count()
        newGroup = Group.objects.get_or_create(name=f"boardgroup{numberOfGroups}")
        newGroup = newGroup[0]
        newGroup.user_set.set(board_users_list)
        return newGroup
    
    def create(self, validated_data):
        board_users = validated_data.pop('board_users', [])
        group = self.create_group(board_users)
        board = Board.objects.create(group=group, **validated_data)
        board.board_users.set(board_users)
        return board

    
class CategorySerializer(serializers.HyperlinkedModelSerializer):
    board = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.IntegerField(required=False)
    class Meta:
        model = Category
        fields= ['name', 'color', 'board', 'id']
        
        
class TaskSerializer(serializers.HyperlinkedModelSerializer):
    category = CategorySerializer()
    assigned_users = UserSerializer(many=True)
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'status', 'category', 'assigned_users', 'priority', 'id']
        
    def create(self, validated_data):
        assigned_users_data = validated_data.pop('assigned_users', [])
        assigned_users = User.objects.filter(id__in=[user.id for user in assigned_users_data])
        category_data = validated_data.pop('category', None)
        category = get_object_or_404(Category, id=category_data['id']) if category_data else None
        board_id = self.context.get('board_id')
        board = get_object_or_404(Board, id=board_id)
        task = Task.objects.create(**validated_data, category=category, board=board)
        task.assigned_users.set(assigned_users)
        return task
        
    def update(self, instance, validated_data):
        assigned_users_data = validated_data.pop('assigned_users', None)
        if assigned_users_data is not None:
            assigned_users = User.objects.filter(id__in=[user.id for user in assigned_users_data])
            instance.assigned_users.set(assigned_users)
        category_data = validated_data.pop('category', None)
        if category_data:
            category = get_object_or_404(Category, id=category_data['id'])
            instance.category = category
        return super().update(instance, validated_data)
    

