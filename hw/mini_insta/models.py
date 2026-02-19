# File: models.py
# Author: Declan Young (declanyg@bu.edu), 2/05/2026
# Description: models file to handle models for mini_insta app

from django.db import models

# Create your models here.
class Profile(models.Model):
    username = models.CharField(max_length=150, unique=True)
    display_name = models.CharField(max_length=150)
    profile_image_url = models.URLField(blank=True)
    bio_text = models.TextField(blank=True)
    join_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.username
    
    def get_all_posts(self):
        return self.posts.all().order_by('-timestamp')

class Post(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='posts')
    timestamp = models.DateTimeField(auto_now_add=True)
    caption = models.TextField(blank=True)

    def __str__(self):
        return self.profile.username + " - " + self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    def get_all_photos(self):
        return self.photos.all().order_by('-timestamp')

class Photo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='photos')
    image_url = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.profile.username + " - " + self.image_url