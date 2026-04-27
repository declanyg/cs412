from django.shortcuts import render
from .models import Customer, Restaurant, MenuItem, Order, OrderItem, Review
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.urls import reverse

# Create your views here.
class ProfileLoginRequiredMixin(LoginRequiredMixin):
    login_url = "final_project:login"

    def get_customer(self):
        return Customer.objects.get(account=self.request.user)

class RestaurantListView(ListView):
    model = Restaurant
    template_name = "final_project/show_all_restaurants.html"
    context_object_name = "restaurants"

class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = "final_project/show_restaurant.html"
    context_object_name = "restaurant"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category_list"] = self.object.get_menu_by_category()
        return context

class CreateCustomerView(CreateView):
    model = Customer
    fields = ['first_name', 'last_name', 'email']
    template_name = "final_project/create_profile_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["user_registration_form"] = UserCreationForm()
        return context
    
    def form_valid(self, form):
        user_form = UserCreationForm(self.request.POST)
        if user_form.is_valid():
            user = user_form.save()

            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

            customer = form.save(commit=False)
            customer.account = user
            customer.save()
            
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('final_project:show_profile')

class UpdateCustomerView(ProfileLoginRequiredMixin, UpdateView):
    model = Customer
    fields = ['first_name', 'last_name', 'email', 'image']
    template_name = "final_project/update_customer_form.html"

    def get_success_url(self):
        return reverse('final_project:show_profile')
    
    def get_object(self, queryset=None):
        return self.get_customer()

class CustomerDetailView(ProfileLoginRequiredMixin, DetailView):
    model = Customer
    template_name = "final_project/show_customer.html"
    context_object_name = "customer"

    def get_object(self, queryset=None):
        return self.get_customer()