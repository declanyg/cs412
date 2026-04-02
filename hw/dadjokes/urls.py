# File: urls.py
# Author: Declan Young (declanyg@bu.edu), 4/1/2026
# Description: urls file to handle routing for dadjokes app

from django.urls import path

from . import views
import django.contrib.auth.views as auth_views
from django.views.generic import TemplateView

app_name = 'dadjokes' 

urlpatterns = [
    path("", views.random_joke, name="index"),
    path("random", views.random_joke, name="show_random_joke"),
    path("jokes/", views.JokeListView.as_view(), name="show_all_jokes"),
    path("joke/<int:pk>/", views.JokeDetailView.as_view(), name="show_joke"),
    path("pictures/", views.PictureListView.as_view(), name="show_all_pictures"),
    path("picture/<int:pk>/", views.PictureDetailView.as_view(), name="show_picture"),

    path('api/', views.api_random_joke),
    path('api/random', views.api_random_joke),
    path('api/jokes', views.api_jokes),
    path('api/joke/<int:pk>', views.api_joke_detail),
    path('api/pictures', views.api_pictures),
    path('api/picture/<int:pk>', views.api_picture_detail),
    path('api/random_picture', views.api_random_picture),
]