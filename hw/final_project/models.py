from collections import defaultdict

from django.db import models

# Create your models here.
class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to="final_project/customers/", blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True)
    account = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='customer')

    def __str__(self):
        return self.last_name + ", " + self.first_name

class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    cuisine = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    hours = models.CharField(max_length=100)
    image = models.ImageField(upload_to="final_project/", blank=True, null=True)

    def get_menu_by_category(self):
        category_list = defaultdict(list)
        for item in self.menu_items.all():
            category_list[item.category].append(item)
        return dict(category_list)

    def get_average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return None
        total_rating = sum(review.rating for review in reviews)
        return total_rating / len(reviews)

    def get_num_reviews(self):
        return self.reviews.count()

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=100)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.restaurant.name + " - " + self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    delivery_address = models.CharField(max_length=300)
    status = models.CharField(max_length=50, default='in cart')

    def __str__(self):
        return f"Order {self.id} by {self.customer.first_name} at {self.restaurant.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    special_instructions = models.TextField(blank=True)

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} for Order {self.order.id}"

class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer.first_name} for {self.restaurant.name}"