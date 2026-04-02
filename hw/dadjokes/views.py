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

def cors_response(data, status=200):
    response = Response(data, status=status)
    response["Access-Control-Allow-Origin"] = "http://localhost:8081"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@api_view(['GET', 'OPTIONS'])
def api_random_joke(request):
    if request.method == 'OPTIONS':
        return cors_response({})
    
    jokes = Joke.objects.all()
    joke = random.choice(jokes) if jokes else None

    if joke:
        serializer = JokeSerializer(joke)
        return cors_response(serializer.data)
    return cors_response({"error": "No jokes found"}, status=404)

@api_view(['GET', 'POST', 'OPTIONS'])
def api_jokes(request):
    if request.method == 'OPTIONS':
        return cors_response({})

    if request.method == 'GET':
        jokes = Joke.objects.all()
        serializer = JokeSerializer(jokes, many=True)
        return cors_response(serializer.data)

    elif request.method == 'POST':
        serializer = JokeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return cors_response(serializer.data, status=201)
        return cors_response(serializer.errors, status=400)

@api_view(['GET', 'OPTIONS'])
def api_joke_detail(request, pk):
    if request.method == 'OPTIONS':
        return cors_response({})

    try:
        joke = Joke.objects.get(pk=pk)
    except Joke.DoesNotExist:
        return cors_response({"error": "Not found"}, status=404)

    serializer = JokeSerializer(joke)
    return cors_response(serializer.data)

@api_view(['GET', 'OPTIONS'])
def api_pictures(request):
    if request.method == 'OPTIONS':
        return cors_response({})

    pictures = Picture.objects.all()
    serializer = PictureSerializer(pictures, many=True)
    return cors_response(serializer.data)

@api_view(['GET', 'OPTIONS'])
def api_picture_detail(request, pk):
    if request.method == 'OPTIONS':
        return cors_response({})

    try:
        picture = Picture.objects.get(pk=pk)
    except Picture.DoesNotExist:
        return cors_response({"error": "Not found"}, status=404)

    serializer = PictureSerializer(picture)
    return cors_response(serializer.data)

@api_view(['GET', 'OPTIONS'])
def api_random_picture(request):
    if request.method == 'OPTIONS':
        return cors_response({})

    pictures = Picture.objects.all()
    picture = random.choice(pictures) if pictures else None

    if picture:
        serializer = PictureSerializer(picture)
        return cors_response(serializer.data)
    return cors_response({"error": "No pictures found"}, status=404)