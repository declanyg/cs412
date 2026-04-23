from django.urls import path

from . import views

app_name = 'final_project' 

urlpatterns = [
    path("", views.RestaurantListView.as_view(), name="index"),
    path("restaurants/", views.RestaurantListView.as_view(), name="show_all_restaurants"),
    path("restaurants/<int:restaurant_id>/", views.RestaurantDetailView.as_view(), name="show_restaurant"),
]