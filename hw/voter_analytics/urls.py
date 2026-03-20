from django.urls import path

from . import views

app_name = 'voter_analytics' 

urlpatterns = [
    path("", views.main, name="main"),
]