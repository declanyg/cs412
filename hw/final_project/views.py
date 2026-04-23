from django.shortcuts import render
from .models import Customer, Restaurant, MenuItem, Order, OrderItem, Review
from django.views.generic import ListView

# Create your views here.
class RestaurantListView(ListView):
    model = Restaurant
    template_name = "final_project/show_all_restaurants.html"
    context_object_name = "restaurants"

class RestaurantDetailView(ListView):
    model = Restaurant
    template_name = "final_project/show_restaurant.html"
    context_object_name = "restaurant"

    def get_queryset(self):
        restaurant_id = self.kwargs.get("restaurant_id")
        return Restaurant.objects.filter(pk=restaurant_id)