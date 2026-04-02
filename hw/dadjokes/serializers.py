# File: serializers.py
# Author: Declan Young (declanyg@bu.edu), 4/1/2026
# Description: serializers file to handle serialization for dadjokes app

from rest_framework import serializers
from .models import Joke, Picture

class JokeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Joke
        fields = '__all__'

class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = '__all__'