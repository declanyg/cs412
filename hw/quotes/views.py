from django.shortcuts import render
import random
import time

# Create your views here.
from django.http import HttpResponse

display_quotes  = ["Appear weak when you are strong, and strong when you are weak.", "The supreme art of war is to subdue the enemy without fighting.", "The greatest victory is that which requires no battle."]
display_quote_images = ["https://upload.wikimedia.org/wikipedia/commons/c/cf/%E5%90%B4%E5%8F%B8%E9%A9%AC%E5%AD%99%E6%AD%A6.jpg", "https://now.tufts.edu/sites/default/files/styles/large_1366w_912h/public/uploaded-assets/images/2023-06/230616_art_war_new_illo_lg.jpg?h=947df58a&itok=WBjecA_n", "https://miro.medium.com/v2/resize:fit:1366/format:webp/1*9hHF2d6D3pMOSuJT3hk9zw.png"]

def index(request):
    random_index = random.randint(0, len(display_quotes) - 1)

    context = {
        "quote_source": display_quotes[random_index],
        "image_source": display_quote_images[random_index],
        "generated_time": time.ctime()
    }

    return render(request, "index.html", context)

def show_all(request):
    context = {
        "quotes": display_quotes,
        "images": display_quote_images,
        "generated_time": time.ctime()
    }

    return render(request, "show_all.html", context)

def about(request):
    context = {
        "generated_time": time.ctime()
    }

    return render(request, "about.html", context)
