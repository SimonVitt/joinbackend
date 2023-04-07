from rest_framework.permissions import BasePermission

from board.models import Board

class IsBoardgroupMember(BasePermission):
    
    def has_permission(self, request, view):
        board_id = view.kwargs.get('id')
        board = Board.objects.get(id=board_id)
        return request.user.groups.filter(id=board.group.id).exists()