from django.contrib import admin
from .models import Category, Board, Task

# Register your models here.
admin.site.register(Category)
admin.site.register(Board)
admin.site.register(Task)
