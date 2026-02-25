# File: urls.py
# Author: Declan Young (declanyg@bu.edu), 2/05/2026
# Description: urls file to handle routing for mini_insta app

from django.urls import path

from . import views

app_name = 'mini_insta' 

urlpatterns = [
    path("", views.ProfileListView.as_view(), name="show_all_profiles"),
    path("profile/<int:pk>/", views.ProfileDetailView.as_view(), name="show_profile"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="show_post"),
    path("profile/<int:pk>/create_post/", views.CreatePostView.as_view(), name="create_post"),
    path("profile/<int:pk>/update/", views.UpdateProfileView.as_view(), name="update_profile"),
    path("post/<int:pk>/delete/", views.DeletePostView.as_view(), name="delete_post"),
    path("post/<int:pk>/update/", views.UpdatePostView.as_view(), name="update_post"),

    path("profile/<int:pk>/followers/", views.ShowFollowersDetailView.as_view(), name="show_followers"),
    path("profile/<int:pk>/following/", views.ShowFollowingDetailView.as_view(), name="show_following"),

    path("profile/<int:pk>/feed/", views.PostFeedListView.as_view(), name="show_feed"),
]