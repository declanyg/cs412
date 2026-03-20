# File: urls.py
# Author: Declan Young (declanyg@bu.edu), 3/19/2026
# Description: urls file to handle routing for voter_analytics app

from django.urls import path

from . import views

app_name = 'voter_analytics' 

urlpatterns = [
    path("", views.VoterAnalyticsView.as_view(), name="voters"),
    path("voter/<int:pk>/", views.VoterDetailView.as_view(), name="voter"),
    path("graphs", views.VoterGraphsView.as_view(), name="graphs"),
]