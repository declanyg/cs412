# File: urls.py
# Author: Declan Young (declanyg@bu.edu), 20/04/2026
# Description: urls file to handle url paths for final_project app

from django.urls import path

from . import views
import django.contrib.auth.views as auth_views
from django.views.generic import TemplateView

app_name = 'final_project' 

urlpatterns = [
    path("", views.RestaurantListView.as_view(), name="index"),
    path("restaurants/", views.RestaurantListView.as_view(), name="show_all_restaurants"),
    path("restaurants/<int:pk>/", views.RestaurantDetailView.as_view(), name="show_restaurant"),

    path('cart/', views.ShowCartView.as_view(), name='show_cart'),
    path("cart/item/add/<int:pk>/", views.AddToCartView.as_view(), name="add_to_cart"),
    path("cart/item/decrement/<int:pk>/", views.DecrementFromCartView.as_view(), name="decrement_from_cart"),
    path('cart/item/delete/<int:pk>/', views.DeleteOrderItemView.as_view(), name='delete_order_item'),
    path("cart/item/edit/<int:pk>/", views.EditOrderItemView.as_view(), name="edit_order_item"),
    path('cart/order/place/<int:pk>/', views.PlaceOrderView.as_view(), name='place_order'),
    path('cart/order/delete/<int:pk>/', views.DeleteOrderView.as_view(), name='delete_order'),
    path('cart/order/confirmation/<int:pk>/', views.OrderConfirmationView.as_view(), name='order_confirmation'),

    path("orders/", views.ShowOrdersView.as_view(), name="show_orders"),
    path("orders/<int:pk>/status/", views.OrderStatusView.as_view(), name="order_status"),
    path("restaurants/<int:pk>/review/", views.WriteReviewView.as_view(), name="write_review"),
    path("reviews/<int:pk>/edit/", views.EditReviewView.as_view(), name="edit_review"),
    path("reviews/<int:pk>/delete/", views.DeleteReviewView.as_view(), name="delete_review"),

    path("login/", auth_views.LoginView.as_view(template_name='final_project/login.html'), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page='final_project:logged_out'), name="logout"),
    path("logged_out/", TemplateView.as_view(template_name='final_project/logged_out.html'), name="logged_out"),
    path("update_customer/", views.UpdateCustomerView.as_view(), name="update_customer"),
    path("customer/", views.CustomerDetailView.as_view(), name="show_customer"),
    path("create_customer/", views.CreateCustomerView.as_view(), name="create_customer"),
]