# File: urls.py
# Author: Declan Young (declanyg@bu.edu), 2/05/2026
# Description: urls file to handle routing for mini_insta app

from django.urls import path

from . import views
import django.contrib.auth.views as auth_views
from django.views.generic import TemplateView

app_name = 'mini_insta' 

urlpatterns = [
    path("", views.ProfileListView.as_view(), name="show_all_profiles"),
    path("profile/<int:pk>/", views.ProfileDetailView.as_view(), name="show_profile"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="show_post"),
    path("profile/create_post/", views.CreatePostView.as_view(), name="create_post"),
    path("profile/update/", views.UpdateProfileView.as_view(), name="update_profile"),
    path("post/<int:pk>/delete/", views.DeletePostView.as_view(), name="delete_post"),
    path("post/update/", views.UpdatePostView.as_view(), name="update_post"),

    path("profile/<int:pk>/followers/", views.ShowFollowersDetailView.as_view(), name="show_followers"),
    path("profile/<int:pk>/following/", views.ShowFollowingDetailView.as_view(), name="show_following"),

    path("profile/feed/", views.PostFeedListView.as_view(), name="show_feed"),

    path("profile/search/", views.SearchView.as_view(), name="search_results"),

    path("profile/", views.PersonalProfileDetailView.as_view(), name="show_profile"),

    path("login/", auth_views.LoginView.as_view(template_name='mini_insta/login.html'), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page='mini_insta:logged_out'), name="logout"),
    path("logged_out/", TemplateView.as_view(template_name='mini_insta/logged_out.html'), name="logged_out"),

    path("create_profile/", views.CreateProfileView.as_view(), name="create_profile"),
]