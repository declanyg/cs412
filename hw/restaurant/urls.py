from django.urls import path

from . import views

app_name = 'restaurant' 

urlpatterns = [
    path("", views.main, name="main"),
    path('main/', views.main, name='main'),
    path('order/', views.order, name='order'),
    path('confirmation/', views.confirmation, name='confirmation')
]