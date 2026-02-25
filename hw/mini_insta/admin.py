from django.contrib import admin

from .models import Follow, Profile, Post, Photo, Comment, Like
# Register your models here.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Photo)
admin.site.register(Follow)
admin.site.register(Comment)
admin.site.register(Like)