# File: views.py
# Author: Declan Young (declanyg@bu.edu), 20/04/2026
# Description: views file to handle views for final_project app

from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer, Restaurant, MenuItem, Order, OrderItem, Review
from .forms import OrderItemForm, ReviewForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
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
        category_list = self.object.get_menu_by_category()

        cart_quantities = {}
        if self.request.user.is_authenticated:
            customer = Customer.objects.filter(account=self.request.user).first()
            if customer:
                order = Order.objects.filter(customer=customer, restaurant=self.object, status='in cart').first()
                if order:
                    for item in order.order_items.all():
                        cart_quantities[item.menu_item_id] = item.quantity

        for items in category_list.values():
            for item in items:
                item.qty_in_cart = cart_quantities.get(item.pk, 0)

        context["category_list"] = category_list
        return context

class CreateCustomerView(CreateView):
    model = Customer
    fields = ['first_name', 'last_name', 'email', 'image']
    template_name = "final_project/create_customer_form.html"

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
        return reverse('final_project:show_customer')

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Reviews authored by this customer, newest first, with the related
        # restaurant pre-fetched so the template can link back.
        context['reviews'] = (
            self.object.reviews
            .select_related('restaurant')
            .order_by('-timestamp')
        )
        return context


class ShowCartView(ProfileLoginRequiredMixin, ListView):
    model = Order
    template_name = 'final_project/show_cart.html'
    context_object_name = 'orders'

    def get_queryset(self):
        customer = self.get_customer()
        return Order.objects.filter(
            customer=customer,
            status='in cart'
        ).prefetch_related('order_items__menu_item')


class AddToCartView(ProfileLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        customer = self.get_customer()
        item = get_object_or_404(MenuItem, pk=self.kwargs['pk'])

        order, _ = Order.objects.get_or_create(
            customer=customer,
            restaurant=item.restaurant,
            status='in cart',
        )

        order_item, created = OrderItem.objects.get_or_create(order=order, menu_item=item)
        if not created:
            order_item.quantity += 1
            order_item.save()

        return redirect(request.META.get('HTTP_REFERER'))

class DecrementFromCartView(ProfileLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        customer = self.get_customer()
        item = get_object_or_404(MenuItem, pk=self.kwargs['pk'])

        order = Order.objects.filter(
            customer=customer,
            restaurant=item.restaurant,
            status='in cart',
        ).first()

        if order:
            order_item = OrderItem.objects.filter(order=order, menu_item=item).first()
            if order_item:
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                else:
                    order_item.delete()
                    if not order.order_items.exists():
                        order.delete()

        return redirect(request.META.get('HTTP_REFERER'))


class EditOrderItemView(ProfileLoginRequiredMixin, UpdateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'final_project/edit_order_item.html'
    context_object_name = 'order_item'

    def get_success_url(self):
        return reverse('final_project:show_cart')


class PlaceOrderView(ProfileLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=self.kwargs['pk'], customer=self.get_customer())
        delivery_address = request.POST.get('delivery_address', '').strip()

        # Re-render cart with an error if no delivery address provided
        if not delivery_address:
            orders = Order.objects.filter(
                customer=self.get_customer(),
                status='in cart'
            ).prefetch_related('order_items__menu_item')
            return render(request, 'final_project/show_cart.html', {
                'orders': orders,
                'address_error_order': order.pk,
            })

        order.delivery_address = delivery_address
        order.status = 'confirmed'
        order.save()

        return redirect(reverse('final_project:order_confirmation', kwargs={'pk': order.pk}))

class DeleteOrderView(ProfileLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=self.kwargs['pk'], customer=self.get_customer())
        order.delete()
        return redirect(reverse('final_project:show_cart'))

class DeleteOrderItemView(ProfileLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        customer = self.get_customer()
        order_item = get_object_or_404(OrderItem, pk=self.kwargs['pk'], order__customer=customer)
        order = order_item.order
        order_item.delete()

        if not order.order_items.exists():
            order.delete()
        return redirect(reverse('final_project:show_cart'))


class OrderConfirmationView(ProfileLoginRequiredMixin, DetailView):
    model = Order
    template_name = 'final_project/order_confirmation.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(
            customer=self.get_customer()
        ).prefetch_related('order_items__menu_item')
    

class OrderStatusView(ProfileLoginRequiredMixin, DetailView):
    """Shows a step-by-step status timeline for a single order."""
    model = Order
    template_name = 'final_project/order_status.html'
    context_object_name = 'order'

    STATUS_FLOW = [
        ('confirmed', 'Order placed', 'We received your order.'),
        ('preparing', 'Preparing', 'The restaurant is making your food.'),
        ('out for delivery', 'Out for delivery', 'Your courier is on the way.'),
        ('delivered', 'Delivered', 'Enjoy your meal!'),
    ]

    def get_queryset(self):
        return Order.objects.filter(
            customer=self.get_customer(),
        ).prefetch_related('order_items__menu_item')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object
        status = (order.status or '').lower()

        # Compute index of current step. Anything unrecognised falls back to
        # the first step so something still renders sensibly.
        keys = [s[0] for s in self.STATUS_FLOW]
        current_index = keys.index(status) if status in keys else 0

        steps = []
        for i, (key, label, blurb) in enumerate(self.STATUS_FLOW):
            if i < current_index:
                state = 'done'
            elif i == current_index:
                state = 'current'
            else:
                state = 'pending'
            steps.append({'key': key, 'label': label, 'blurb': blurb, 'state': state})

        context['steps'] = steps
        context['is_cancelled'] = status == 'cancelled'
        context['is_complete'] = status == 'delivered'

        existing_review = Review.objects.filter(
            customer=self.get_customer(),
            restaurant=order.restaurant,
        ).first()
        context['existing_review'] = existing_review
        context['review_form'] = ReviewForm(instance=existing_review)
        return context


class WriteReviewView(ProfileLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        customer = self.get_customer()
        restaurant = get_object_or_404(Restaurant, pk=self.kwargs['pk'])

        existing = Review.objects.filter(customer=customer, restaurant=restaurant).first()
        form = ReviewForm(request.POST, instance=existing)

        if form.is_valid():
            review = form.save(commit=False)
            review.customer = customer
            review.restaurant = restaurant
            review.save()

        return redirect(
            request.META.get('HTTP_REFERER')
            or reverse('final_project:show_restaurant', kwargs={'pk': restaurant.pk})
        )


class EditReviewView(ProfileLoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'final_project/edit_review.html'
    context_object_name = 'review'

    def get_queryset(self):
        return Review.objects.filter(customer=self.get_customer())

    def get_success_url(self):
        return reverse('final_project:show_customer')


class DeleteReviewView(ProfileLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        review = get_object_or_404(
            Review,
            pk=self.kwargs['pk'],
            customer=self.get_customer(),
        )
        review.delete()
        return redirect(
            request.META.get('HTTP_REFERER')
            or reverse('final_project:show_customer')
        )


class ShowOrdersView(ProfileLoginRequiredMixin, ListView):
    model = Order
    template_name = 'final_project/show_orders.html'
    context_object_name = 'orders'

    ACTIVE_STATUSES = {'confirmed', 'preparing', 'out for delivery'}

    def get_queryset(self):
        return Order.objects.filter(
            customer=self.get_customer(),
        ).exclude(status='in cart').prefetch_related('order_items__menu_item')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_orders = context['orders']
        context['active_orders'] = [order for order in all_orders if order.status in self.ACTIVE_STATUSES]
        context['past_orders'] = [order for order in all_orders if order.status not in self.ACTIVE_STATUSES]
        return context