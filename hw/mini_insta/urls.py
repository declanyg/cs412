from django.urls import path

from . import views

app_name = 'mini_insta' 

urlpatterns = [
    path("", views.index, name="index"),
    path('show_all_profiles/', views.show_all_profiles, name='show_all_profiles'),
]