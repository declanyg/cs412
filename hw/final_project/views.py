# File: views.py
# Author: Declan Young (declanyg@bu.edu), 20/04/2026
# Description: views file to handle views for final_project app

from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer, Restaurant, MenuItem, Order, OrderItem, Review
from .forms import OrderItemForm, ReviewForm, MenuItemForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.urls import reverse
from django.db.models import Q
from urllib.parse import urlparse


class ProfileLoginRequiredMixin(LoginRequiredMixin):
    """Mixin that enforces login and provides a helper to retrieve the
    Customer profile linked to the currently authenticated user."""

    login_url = "final_project:login"

    def get_customer(self):
        """Return the Customer instance associated with the logged-in user.
        """
        return Customer.objects.get(account=self.request.user)


class RestaurantListView(ListView):
    """Displays a filterable, searchable list of all restaurants.
    """

    model = Restaurant
    template_name = "final_project/show_all_restaurants.html"
    context_object_name = "restaurants"

    def get_queryset(self):
        """Return the filtered queryset of restaurants based on GET parameters.
        """
        qs = Restaurant.objects.all().order_by('name')

        query = (self.request.GET.get('q') or '').strip()
        if query:
            qs = qs.filter(
                Q(name__icontains=query)
                | Q(cuisine__icontains=query)
                | Q(address__icontains=query)
            )

        cuisine = (self.request.GET.get('cuisine') or '').strip()
        if cuisine:
            qs = qs.filter(cuisine__iexact=cuisine)

        return qs

    def get_context_data(self, **kwargs):
        """Adds the distinct list of cuisines for the dropdown, the current
        search query, the selected cuisine, a flag indicating whether any
        """
        context = super().get_context_data(**kwargs)
        context['cuisines'] = (
            Restaurant.objects
            .order_by('cuisine')
            .values_list('cuisine', flat=True)
            .distinct()
        )
        context['query'] = (self.request.GET.get('q') or '').strip()
        context['selected_cuisine'] = (self.request.GET.get('cuisine') or '').strip()
        context['has_filters'] = bool(context['query'] or context['selected_cuisine'])
        context['total_results'] = self.object_list.count()
        return context


class RestaurantDetailView(DetailView):
    """Displays the full detail page for a single restaurant, including its
    categorised menu and customer reviews. Annotates each menu item with
    the quantity currently in the logged-in customer's cart."""

    model = Restaurant
    template_name = "final_project/show_restaurant.html"
    context_object_name = "restaurant"

    def get_context_data(self, **kwargs):
        """Build context with the categorised menu and per-item cart quantities.
        """
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
    """Handles new customer registration. Creates both a Django auth User
    and a linked Customer profile in a single form submission."""

    model = Customer
    fields = ['first_name', 'last_name', 'email', 'image', 'restaurant_owner']
    template_name = "final_project/create_customer_form.html"

    def get_context_data(self, **kwargs):
        """Add the Django UserCreationForm to the template context so that
        username and password fields are rendered alongside the Customer fields.
        """
        context = super().get_context_data(**kwargs)
        context["user_registration_form"] = UserCreationForm()
        return context

    def form_valid(self, form):
        """Creates the auth User first, logs them in immediately, then saves
        the Customer profile linked to that User. If the UserCreationForm
        is invalid the whole submission is rejected.
        """
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
        """Return the URL to redirect to after successful customer creation.
        """
        return reverse('final_project:show_customer')


class UpdateCustomerView(ProfileLoginRequiredMixin, UpdateView):
    """Allows the logged-in customer to update their own profile details."""

    model = Customer
    fields = ['first_name', 'last_name', 'email', 'image', 'restaurant_owner']
    template_name = "final_project/update_customer_form.html"

    def get_success_url(self):
        """Return the URL to redirect to after a successful profile update.
        """
        return reverse('final_project:show_customer')

    def get_object(self, queryset=None):
        """Return the Customer object to be updated.
        """
        return self.get_customer()


class CustomerDetailView(ProfileLoginRequiredMixin, DetailView):
    """Displays the profile page for the currently logged-in customer,
    including their submitted reviews."""

    model = Customer
    template_name = "final_project/show_customer.html"
    context_object_name = "customer"

    def get_object(self, queryset=None):
        """Return the Customer profile for the logged-in user.
        """
        return self.get_customer()

    def get_context_data(self, **kwargs):
        """Add the customer's reviews to the template context, ordered by
        most recent first.
        """
        context = super().get_context_data(**kwargs)
        context['reviews'] = (
            self.object.reviews
            .select_related('restaurant')
            .order_by('-timestamp')
        )
        return context


class ShowCartView(ProfileLoginRequiredMixin, ListView):
    """Displays the logged-in customer's active cart, showing all orders
    with status 'in cart' grouped by restaurant."""

    model = Order
    template_name = 'final_project/show_cart.html'
    context_object_name = 'orders'

    def get_queryset(self):
        """Return all in-cart orders for the logged-in customer
        """
        customer = self.get_customer()
        return Order.objects.filter(
            customer=customer,
            status='in cart'
        ).prefetch_related('order_items__menu_item')


class AddToCartView(ProfileLoginRequiredMixin, View):
    """Handles POST requests to add one unit of a MenuItem to the
    customer's cart. Creates a new Order for the restaurant if one does
    not already exist with status 'in cart'."""

    def post(self, request, *args, **kwargs):
        """Add one unit of the specified MenuItem to the customer's cart.
        """
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
    """Handles POST requests to remove one unit of a MenuItem from the
    customer's cart. Deletes the OrderItem when quantity reaches zero,
    and deletes the parent Order if it becomes empty."""

    def post(self, request, *args, **kwargs):
        """Decrement the quantity of the specified MenuItem in the customer's cart.
        """
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
    """Allows the logged-in customer to edit the quantity and special
    instructions for an existing OrderItem in their cart."""

    model = OrderItem
    form_class = OrderItemForm
    template_name = 'final_project/edit_order_item.html'
    context_object_name = 'order_item'

    def get_success_url(self):
        """Return the URL to redirect to after a successful OrderItem update.
        """
        return reverse('final_project:show_cart')


class PlaceOrderView(ProfileLoginRequiredMixin, View):
    """Handles POST requests to confirm a cart Order."""

    def post(self, request, *args, **kwargs):
        """Confirm the specified Order with the supplied delivery address.
        """
        order = get_object_or_404(Order, pk=self.kwargs['pk'], customer=self.get_customer())
        delivery_address = request.POST.get('delivery_address', '').strip()

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
    """Handles POST requests to delete an entire Order from the customer's cart."""

    def post(self, request, *args, **kwargs):
        """Delete the specified Order and all its OrderItems.
        """
        order = get_object_or_404(Order, pk=self.kwargs['pk'], customer=self.get_customer())
        order.delete()
        return redirect(reverse('final_project:show_cart'))


class DeleteOrderItemView(ProfileLoginRequiredMixin, View):
    """Handles POST requests to remove a single OrderItem from the cart.
    Deletes the parent Order if it becomes empty."""

    def post(self, request, *args, **kwargs):
        """Delete the specified OrderItem from the customer's cart.
        """
        customer = self.get_customer()
        order_item = get_object_or_404(OrderItem, pk=self.kwargs['pk'], order__customer=customer)
        order = order_item.order
        order_item.delete()

        if not order.order_items.exists():
            order.delete()
        return redirect(reverse('final_project:show_cart'))


class OrderConfirmationView(ProfileLoginRequiredMixin, DetailView):
    """Displays the confirmation page for a successfully placed Order,
    summarising the items, total, and delivery address."""

    model = Order
    template_name = 'final_project/order_confirmation.html'
    context_object_name = 'order'

    def get_queryset(self):
        """Return Orders belonging to the logged-in customer with items prefetched.
        """
        return Order.objects.filter(
            customer=self.get_customer()
        ).prefetch_related('order_items__menu_item')


class OrderStatusView(ProfileLoginRequiredMixin, DetailView):
    """Shows a step-by-step status timeline for a single Order, indicating
    which stage of the delivery pipeline the order has reached."""

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
        """Return Orders belonging to the logged-in customer with items prefetched.
        """
        return Order.objects.filter(
            customer=self.get_customer(),
        ).prefetch_related('order_items__menu_item')

    def get_context_data(self, **kwargs):
        """Build the status timeline and attach review form data to context.
        Computes the state for each step.
        """
        context = super().get_context_data(**kwargs)
        order = self.object
        status = (order.status or '').lower()

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
    """Handles POST requests to create or update a customer's Review for
    a Restaurant. Each customer may have at most one review per restaurant;
    submitting again updates the existing review."""

    def post(self, request, *args, **kwargs):
        """Create or update a Review for the specified Restaurant.
        """
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
    """Allows the logged-in customer to edit one of their existing Reviews
    from their profile page."""

    model = Review
    form_class = ReviewForm
    template_name = 'final_project/edit_review.html'
    context_object_name = 'review'

    def get_queryset(self):
        """Return Reviews belonging to the logged-in customer only.
        """
        return Review.objects.filter(customer=self.get_customer())

    def get_success_url(self):
        """Return the URL to redirect to after a successful review update.
        """
        return reverse('final_project:show_customer')


class DeleteReviewView(ProfileLoginRequiredMixin, View):
    """Handles POST requests to delete one of the logged-in customer's Reviews."""

    def post(self, request, *args, **kwargs):
        """Delete the specified Review
        """
        review = get_object_or_404(
            Review,
            pk=self.kwargs['pk'],
            customer=self.get_customer(),
        )
        pk = review.pk
        review.delete()

        deleted_paths = {
            reverse('final_project:edit_review', kwargs={'pk': pk}),
            reverse('final_project:delete_review', kwargs={'pk': pk}),
        }

        referer = request.META.get('HTTP_REFERER') or ''
        referer_path = urlparse(referer).path

        if not referer or referer_path in deleted_paths:
            return redirect('final_project:show_customer')
        return redirect(referer)


class ManageRestaurantsView(ProfileLoginRequiredMixin, ListView):
    """Lists all restaurants owned by the logged-in user, providing links
    to edit, delete, and manage the menu for each."""

    model = Restaurant
    template_name = 'final_project/manage_restaurants.html'
    context_object_name = 'restaurants'

    def get_queryset(self):
        """Return only the restaurants owned by the logged-in user, ordered by name.
        """
        return (
            Restaurant.objects
            .filter(owner=self.request.user)
            .order_by('name')
        )


class CreateRestaurantView(ProfileLoginRequiredMixin, CreateView):
    """Allows a restaurant owner to create a new Restaurant record,
    automatically assigning the logged-in user as the owner."""

    model = Restaurant
    fields = ['name', 'cuisine', 'address', 'hours', 'image']
    template_name = 'final_project/create_restaurant_form.html'

    def form_valid(self, form):
        """Assign the logged-in user as the restaurant owner before saving.
        """
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after a restaurant is created.
        """
        return reverse('final_project:manage_restaurants')


class EditRestaurantView(ProfileLoginRequiredMixin, UpdateView):
    """Allows a restaurant owner to edit the details of one of their
    own Restaurants."""

    model = Restaurant
    fields = ['name', 'cuisine', 'address', 'hours', 'image']
    template_name = 'final_project/edit_restaurant_form.html'
    context_object_name = 'restaurant'

    def get_queryset(self):
        """Return only restaurants owned by the logged-in user.
        """
        return Restaurant.objects.filter(owner=self.request.user)

    def get_success_url(self):
        """Return the URL to redirect to after a successful restaurant update.
        """
        return reverse('final_project:manage_restaurants')


class DeleteRestaurantView(ProfileLoginRequiredMixin, View):
    """Handles POST requests to delete a Restaurant owned by the logged-in user."""

    def post(self, request, *args, **kwargs):
        """Delete the specified Restaurant after verifying ownership.
        """
        restaurant = get_object_or_404(
            Restaurant,
            pk=self.kwargs['pk'],
            owner=request.user,
        )
        restaurant.delete()
        return redirect('final_project:manage_restaurants')


class ManageMenuView(ProfileLoginRequiredMixin, DetailView):
    """Per-restaurant menu management page for the restaurant owner.
    """

    model = Restaurant
    template_name = 'final_project/manage_menu.html'
    context_object_name = 'restaurant'

    def get_queryset(self):
        """Return only restaurants owned by the logged-in user.
        """
        return Restaurant.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        """Add the categorised menu items and a blank create form to context.
        """
        context = super().get_context_data(**kwargs)
        context['categories'] = self.object.get_menu_by_category()
        context['create_form'] = MenuItemForm()
        return context


class CreateMenuItemView(ProfileLoginRequiredMixin, View):
    """Handles POST requests to add a new MenuItem to a restaurant's menu.
    Only the owning user may add items to a restaurant."""

    def post(self, request, *args, **kwargs):
        """Create a new MenuItem linked to the specified Restaurant.
        """
        restaurant = get_object_or_404(
            Restaurant,
            pk=self.kwargs['pk'],
            owner=request.user,
        )
        form = MenuItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.restaurant = restaurant
            item.save()
        return redirect('final_project:manage_menu', pk=restaurant.pk)


class EditMenuItemView(ProfileLoginRequiredMixin, UpdateView):
    """Allows a restaurant owner to edit the details of one of their
    MenuItems."""

    model = MenuItem
    form_class = MenuItemForm
    template_name = 'final_project/edit_menu_item_form.html'
    context_object_name = 'menu_item'

    def get_queryset(self):
        """Return only MenuItems belonging to restaurants owned by the logged-in user.
        """
        return MenuItem.objects.filter(restaurant__owner=self.request.user)

    def get_success_url(self):
        """Return the URL to redirect to after a successful menu item update.
        """
        return reverse('final_project:manage_menu', kwargs={'pk': self.object.restaurant.pk})


class DeleteMenuItemView(ProfileLoginRequiredMixin, View):
    """Handles POST requests to delete a MenuItem from a restaurant's menu.
    """

    def post(self, request, *args, **kwargs):
        """Delete the specified MenuItem after verifying ownership.
        """
        item = get_object_or_404(
            MenuItem,
            pk=self.kwargs['pk'],
            restaurant__owner=request.user,
        )
        restaurant_pk = item.restaurant.pk
        item.delete()
        return redirect('final_project:manage_menu', pk=restaurant_pk)


class ToggleMenuItemAvailabilityView(ProfileLoginRequiredMixin, View):
    """Handles POST requests to flip the available flag on a MenuItem,
    making it visible or hidden on the public restaurant page."""

    def post(self, request, *args, **kwargs):
        """Toggle the availability of the specified MenuItem.
        """
        item = get_object_or_404(
            MenuItem,
            pk=self.kwargs['pk'],
            restaurant__owner=request.user,
        )
        item.available = not item.available
        item.save()
        return redirect('final_project:manage_menu', pk=item.restaurant.pk)


ORDER_STATUS_CHOICES = [
    ('confirmed', 'Confirmed'),
    ('preparing', 'Preparing'),
    ('out for delivery', 'Out for delivery'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
]
ACTIVE_OWNER_STATUSES = {'confirmed', 'preparing', 'out for delivery'}


class ManageOrdersView(ProfileLoginRequiredMixin, ListView):
    """Displays all incoming orders for restaurants owned by the logged-in
    user, split into active and completed groups."""

    model = Order
    template_name = 'final_project/manage_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        """Return all non-cart orders for the logged-in owner's restaurants
        """
        return (
            Order.objects
            .filter(restaurant__owner=self.request.user)
            .exclude(status='in cart')
            .select_related('customer', 'restaurant')
            .prefetch_related('order_items__menu_item')
            .order_by('-id')
        )

    def get_context_data(self, **kwargs):
        """Split orders into active and completed groups and add status choices.
        """
        context = super().get_context_data(**kwargs)
        all_orders = context['orders']
        context['active_orders'] = [order for order in all_orders if order.status in ACTIVE_OWNER_STATUSES]
        context['completed_orders'] = [order for order in all_orders if order.status not in ACTIVE_OWNER_STATUSES]
        context['status_choices'] = ORDER_STATUS_CHOICES
        return context


class UpdateOrderStatusView(ProfileLoginRequiredMixin, View):
    """Handles POST requests from restaurant owners to advance or update
    the status of a specific Order."""

    def post(self, request, *args, **kwargs):
        """Update the status of the specified Order.
        """
        order = get_object_or_404(
            Order,
            pk=self.kwargs['pk'],
            restaurant__owner=request.user,
        )
        new_status = (request.POST.get('status') or '').strip().lower()
        valid_statuses = {key for key, _ in ORDER_STATUS_CHOICES}
        if new_status in valid_statuses:
            order.status = new_status
            order.save()
        return redirect('final_project:manage_orders')


class ShowOrdersView(ProfileLoginRequiredMixin, ListView):
    """Displays the logged-in customer's order history, split into active
    orders and past orders."""

    model = Order
    template_name = 'final_project/show_orders.html'
    context_object_name = 'orders'

    ACTIVE_STATUSES = {'confirmed', 'preparing', 'out for delivery'}

    def get_queryset(self):
        """Return all placed orders for the logged-in customer, excluding
        in-cart orders
        """
        return Order.objects.filter(
            customer=self.get_customer(),
        ).exclude(status='in cart').prefetch_related('order_items__menu_item')

    def get_context_data(self, **kwargs):
        """Split orders into active and past groups for the template.
        """
        context = super().get_context_data(**kwargs)
        all_orders = context['orders']
        context['active_orders'] = [order for order in all_orders if order.status in self.ACTIVE_STATUSES]
        context['past_orders'] = [order for order in all_orders if order.status not in self.ACTIVE_STATUSES]
        return context
