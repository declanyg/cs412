# File: models.py
# Author: Declan Young (declanyg@bu.edu), 4/1/2026
# Description: models file to handle models for dadjokes app

from django.db import models

# Create your models here.
class Joke(models.Model):
    joke_text = models.TextField()
    contributor_name = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.joke_text + " - " + self.contributor_name
    
class Picture(models.Model):
    contributor_name = models.TextField()
    image_url = models.URLField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.contributor_name + " - " + self.image_url