from django.shortcuts import render
import random
import time
import datetime

# Create your views here.
from django.http import HttpResponse

def main(request):

    context = {
        "image_source": "https://chatgpt.com/backend-api/estuary/public_content/enc/eyJpZCI6Im1fNjk3Yjk0MDkyMjljODE5MWIxODhiZTBkNDcxMzM0MGI6ZmlsZV8wMDAwMDAwMDIwZTQ3MWY4ODVmOWFhYTU2M2UxMjM5OCIsInRzIjoiMjA0ODIiLCJwIjoicHlpIiwiY2lkIjoiMSIsInNpZyI6IjI4ZmQ0N2E2NDg3NzZkMTJlMjkyYmY3ZGQzYjkzMTM2ZDcwM2FmYWFhMTY4ODc2YjVkZWMzMTNiMmJhZWNjOWQiLCJ2IjoiMCIsImdpem1vX2lkIjpudWxsLCJjcyI6bnVsbCwiY3AiOm51bGwsIm1hIjpudWxsfQ==",
        "generated_time": time.ctime()
    }

    return render(request, "restaurant/main.html", context)

def order(request):
    weekday = datetime.datetime.today().weekday()
    daily_specials = [
        "Banana Split $3.00",
        "Banana Pancake $2.75",
        "Banana Oatmeal Cookie $2.50",
        "Banana Muffin $2.25",
        "Fried Bananas $2.00",
        "Banana Pudding $3.50",
        "Banana Foster $4.00"
    ]

    context = {
        "daily_special": daily_specials[weekday],
        "generated_time": time.ctime()
    }

    return render(request, "restaurant/order.html", context)

def confirmation(request):
    context = {
        "generated_time": time.ctime()
    }

    return render(request, "restaurant/confirmation.html", context)
