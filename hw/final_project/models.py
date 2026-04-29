# File: models.py
# Author: Declan Young (declanyg@bu.edu), 20/04/2026
# Description: models file to handle models for final_project app

from collections import defaultdict
from django.db import models

class Customer(models.Model):
    """Represents a customer in the system, linked to a Django auth User account.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to="final_project/customers/", blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True)
    restaurant_owner = models.BooleanField(default=False)
    account = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='customer')

    def __str__(self):
        """Return a string representation of the customer.
        """
        return self.last_name + ", " + self.first_name
    

class Restaurant(models.Model):
    """Represents a restaurant in the system, owned by a Customer.
    """
    name = models.CharField(max_length=200)
    cuisine = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    hours = models.CharField(max_length=100)
    image = models.ImageField(upload_to="final_project/", blank=True, null=True)

    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='owned_restaurants')

    def get_menu_by_category(self):
        """Return the restaurant's menu items grouped by category.
        """
        category_list = defaultdict(list)
        for item in self.menu_items.all():
            category_list[item.category].append(item)
        return dict(category_list)

    def get_average_rating(self):
        """Calculate and return the average rating for the restaurant based on its reviews.
        """
        reviews = self.reviews.all()
        if not reviews:
            return None
        total_rating = sum(review.rating for review in reviews)
        return total_rating / len(reviews)

    def get_num_reviews(self):
        """Return the total number of reviews for the restaurant.
        """
        return self.reviews.count()

    def __str__(self):
        """Return the restaurant's name as its string representation.
        """
        return self.name


class MenuItem(models.Model):
    """Represents a menu item offered by a restaurant.
    """
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=100)
    available = models.BooleanField(default=True)

    def __str__(self):
        """Return a string representation of the menu item.
        """
        return self.restaurant.name + " - " + self.name


class Order(models.Model):
    """Represents a customer's order at a restaurant, which can contain multiple menu items.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    delivery_address = models.CharField(max_length=300)
    status = models.CharField(max_length=50, default='in cart')

    def __str__(self):
        """Return a string representation of the order.
        """
        return f"Order {self.id} by {self.customer.first_name} at {self.restaurant.name}"
    
    def get_total(self):
        """Calculate and return the total price of the order by summing the price of each menu item multiplied by its quantity.
        """
        return sum(item.menu_item.price * item.quantity for item in self.order_items.all())


class OrderItem(models.Model):
    """Represents a specific menu item and quantity within an order, along with any special instructions.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    special_instructions = models.TextField(blank=True)

    def __str__(self):
        """Return a string representation of the order item.
        """
        return f"{self.quantity} x {self.menu_item.name} for Order {self.order.id}"


class Review(models.Model):
    """Represents a customer's review of a restaurant, including a rating and optional comment.
    """
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the review.
        """
        return f"Review by {self.customer.first_name} for {self.restaurant.name}"