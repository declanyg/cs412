from django.urls import path

from . import views
import django.contrib.auth.views as auth_views

app_name = 'final_project' 

urlpatterns = [
    path("", views.RestaurantListView.as_view(), name="index"),
    path("restaurants/", views.RestaurantListView.as_view(), name="show_all_restaurants"),
    path("restaurants/<int:pk>/", views.RestaurantDetailView.as_view(), name="show_restaurant"),

    path("login/", auth_views.LoginView.as_view(template_name='final_project/login.html'), name="login"),
    path("update_customer/", views.UpdateCustomerView.as_view(), name="update_customer"),
    path("customer/", views.CustomerDetailView.as_view(), name="show_customer"),
    path("create_customer/", views.CreateCustomerView.as_view(), name="create_customer"),
]