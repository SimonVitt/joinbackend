from django.contrib.auth.models import User, Group
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
    group = GroupSerializer()
    class Meta:
        model = Board
        fields = ['name', 'group', 'board_users', 'id']
        
    def update(self, instance, validated_data):
        new_board_users = validated_data.pop("board_users", None)
        if new_board_users:
            instance.group.user_set.set(new_board_users)
            instance.board_users.set(new_board_users)
        return super().update(instance, validated_data)

    
class CategorySerializer(serializers.HyperlinkedModelSerializer):
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())
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
        
    def update(self, instance, validated_data):
        assigned_users_data = validated_data.get('assigned_users', None)
        if(assigned_users_data != None):
            del validated_data['assigned_users']
            assigned_users = []
            for user in assigned_users_data:
                assigned_users.append(user)
            instance.assigned_users.set(assigned_users)
        category = validated_data.get('category', None)
        if(category):
            del validated_data['category']
            category_id = category.get('id')
            if category_id:
                category = Category.objects.get(id=category_id)
                instance.category = category
        return super().update(instance, validated_data)
    

