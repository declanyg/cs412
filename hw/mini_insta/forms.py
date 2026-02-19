# File: forms.py
# Author: Declan Young (declanyg@bu.edu), 02/19/2026
# Description: forms file to handle form definitions for mini_insta app

from django import forms
from .models import *

class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption']