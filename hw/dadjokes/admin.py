# File: admin.py
# Author: Declan Young (declanyg@bu.edu), 4/1/2026
# Description: admin file to handle admin logic for dadjokes app

from django.contrib import admin

from .models import Joke, Picture

# Register your models here.
admin.site.register(Joke)
admin.site.register(Picture)