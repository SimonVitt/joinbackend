from django.urls import include, path
from .views import BoardViewSet, CategoryViewSet, TaskViewSet, UserView
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'boards', BoardViewSet, basename='boards')
router.register(r'boards/(?P<id>[\w-]+)/tasks', TaskViewSet, basename='boardtasks')
router.register(r'boards/(?P<id>[\w-]+)/categories', CategoryViewSet, basename='boardcategories')

urlpatterns = [
    path('users/', UserView.as_view()),
    path('boards/<int:id>/users/', UserView.as_view()),
    path('', include(router.urls))
]