from django.shortcuts import render
import random
import time
import datetime

# Create your views here.
daily_specials = [
        "Banana Split $3.00",
        "Banana Pancake $2.75",
        "Banana Oatmeal Cookie $2.50",
        "Banana Muffin $2.25",
        "Fried Bananas $2.00",
        "Banana Pudding $3.50",
        "Banana Foster $4.00"
    ]
prices = {
    'Banana': 1.00,
    'Peeled Banana': 1.50,
    'Banana Smoothie': 2.00,
    'Banana Bread': 2.50,
    'Banana Cream Pie': 5.00,
    #Specials
    'Banana Split': 3.00,
    'Banana Pancake': 2.75,
    'Banana Oatmeal Cookie': 2.50,
    'Banana Muffin': 2.25,
    'Fried Bananas': 2.00,
    'Banana Pudding': 3.50,
    'Banana Foster': 4.00
}

def main(request):

    context = {
        "image_source": "https://i.postimg.cc/506C5LCq/banana-store.png",
        "generated_time": time.ctime()
    }

    return render(request, "restaurant/main.html", context)

def order(request):

    weekday = datetime.datetime.today().weekday()
    daily_special = daily_specials[weekday]
    context = {
        "daily_special": daily_special,
        "generated_time": time.ctime()
    }

    return render(request, "restaurant/order.html", context)

def confirmation(request):
    weekday = datetime.datetime.today().weekday()
    weekly_special = daily_specials[weekday].split(" $")[0]
    total = 0.0

    context = {}

    if request.method == 'POST':
        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        special_instructions = request.POST.get('special instruction', '')

        items = []
        for item_name in ['Banana', 'Peeled Banana', 'Banana Smoothie', 'Banana Bread', 'Banana Cream Pie']:
            if request.POST.get(item_name):
                items.append(f"{item_name} ${prices[item_name]:.3f}")
                total += prices[item_name]
        if request.POST.get('Daily Special'):
            items.append(f"{weekly_special} ${prices[weekly_special]:.3f}")
            total += prices[weekly_special]

        context = {
            'name': name,
            'phone': phone,
            'email': email,
            'special_instructions': special_instructions,
            'items': items,
            'total': total,
            "generated_time": time.ctime()
        }

    return render(request, 'restaurant/confirmation.html', context)
