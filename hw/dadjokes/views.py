# File: views.py
# Author: Declan Young (declanyg@bu.edu), 4/1/2026
# Description: views file to handle logic for dadjokes app

from django.shortcuts import render
from django.views.generic import ListView, DetailView
import random

from .models import Joke, Picture

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import JokeSerializer, PictureSerializer

# Create your views here.

def random_joke(request):
    jokes = Joke.objects.all()
    pictures = Picture.objects.all()
    
    joke = random.choice(jokes) if jokes else None
    picture = random.choice(pictures) if pictures else None

    context = {
        "joke": joke,
        "picture": picture
    }

    return render(request, "dadjokes/random_joke.html", context)

class JokeListView(ListView):
    model = Joke
    template_name = "dadjokes/show_all_jokes.html"
    context_object_name = "joke_list"

class JokeDetailView(DetailView):
    model = Joke
    template_name = "dadjokes/show_joke.html"
    context_object_name = "joke"

class PictureListView(ListView):
    model = Picture
    template_name = "dadjokes/show_all_pictures.html"
    context_object_name = "picture_list"

class PictureDetailView(DetailView):
    model = Picture
    template_name = "dadjokes/show_picture.html"
    context_object_name = "picture"


#Api Definitions
@api_view(['GET'])
def api_random_joke(request):
    jokes = Joke.objects.all()
    joke = random.choice(jokes) if jokes else None

    if joke:
        serializer = JokeSerializer(joke)
        return Response(serializer.data)
    return Response({"error": "No jokes found"}, status=404)

@api_view(['GET', 'POST'])
def api_jokes(request):
    if request.method == 'GET':
        jokes = Joke.objects.all()
        serializer = JokeSerializer(jokes, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = JokeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET'])
def api_joke_detail(request, pk):
    try:
        joke = Joke.objects.get(pk=pk)
    except Joke.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    serializer = JokeSerializer(joke)
    return Response(serializer.data)

@api_view(['GET'])
def api_pictures(request):
    pictures = Picture.objects.all()
    serializer = PictureSerializer(pictures, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_picture_detail(request, pk):
    try:
        picture = Picture.objects.get(pk=pk)
    except Picture.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    serializer = PictureSerializer(picture)
    return Response(serializer.data)

@api_view(['GET'])
def api_random_picture(request):
    pictures = Picture.objects.all()
    picture = random.choice(pictures) if pictures else None

    if picture:
        serializer = PictureSerializer(picture)
        return Response(serializer.data)
    return Response({"error": "No pictures found"}, status=404)