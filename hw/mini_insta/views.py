import time
from django.shortcuts import render

# Create your views here.
def index(request):

    context = {
        "generated_time": time.ctime()
    }

    return render(request, "mini_insta/index.html", context)

def show_all_profiles(request):
    context = {
        "generated_time": time.ctime()
    }

    return render(request, "mini_insta/show_all_profiles.html", context)
