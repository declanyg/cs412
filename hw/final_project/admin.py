# File: admin.py
# Author: Declan Young (declanyg@bu.edu), 20/04/2026
# Description: admin file to handle admin interface for final_project app

from django.contrib import admin

from .models import Customer, MenuItem, Order, OrderItem, Restaurant, Review

# Register your models here.
admin.site.register(Customer)
admin.site.register(Restaurant)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)