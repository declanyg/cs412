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
    
    def get_followers(self):
        return [follow.follower_profile for follow in self.profile.all()]
    
    def get_num_followers(self):
        return self.profile.count()
    
    def get_following(self):
        return [follow.profile for follow in self.follower_profile.all()]
    
    def get_num_following(self):
        return self.follower_profile.count()

    def get_post_feed(self):
        following_profiles = self.get_following()
        return Post.objects.filter(profile__in=following_profiles).order_by('-timestamp')

class Post(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='posts')
    timestamp = models.DateTimeField(auto_now_add=True)
    caption = models.TextField(blank=True)

    def __str__(self):
        return self.profile.username + " - " + self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    def get_all_photos(self):
        return self.photos.all().order_by('-timestamp')

    def get_all_comments(self):
        return self.comments.all().order_by('-timestamp')
    
    def get_likes(self):
        return self.likes.all().order_by('-timestamp')

class Photo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='photos')
    image_url = models.URLField(blank=True)
    image_file = models.ImageField(upload_to="mini_insta/", blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.profile.username + " - " + (self.image_url if self.image_url else self.image_file.url)
    
    def get_image_url(self):
        if self.image_url:
            return self.image_url
        return self.image_file.url

class Follow(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile')
    follower_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='follower_profile')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.follower_profile.username + " follows " + self.profile.username

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    def __str__(self):
        return self.profile.username + " commented on " + self.post.profile.username + "'s post on " + self.timestamp.strftime("%Y-%m-%d %H:%M:%S")

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.profile.username + " liked " + self.post.profile.username + "'s post on " + self.timestamp.strftime("%Y-%m-%d %H:%M:%S")