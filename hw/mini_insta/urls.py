# File: urls.py
# Author: Declan Young (declanyg@bu.edu), 3/05/2026
# Description: urls file to handle routing for mini_insta app

from django.urls import path

from . import views

app_name = 'mini_insta' 

urlpatterns = [
    path("", views.ProfileListView.as_view(), name="show_all_profiles"),
    path("profile/<int:pk>/", views.ProfileDetailView.as_view(), name="show_profile"),
]