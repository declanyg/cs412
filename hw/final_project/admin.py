from django.contrib import admin

from .models import Customer, MenuItem, Order, OrderItem, Restaurant, Review

# Register your models here.
admin.site.register(Customer)
admin.site.register(Restaurant)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)