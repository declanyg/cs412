import time
from django.shortcuts import render
from django.views.generic import ListView
from .models import Profile

# Create your views here.
class ProfileListView(ListView):
    model = Profile
    template_name = "mini_insta/show_all_profiles.html"
    context_object_name = "profiles"

def show_profile(request):
    context = {
        "generated_time": time.ctime()
    }

    return render(request, "mini_insta/profile_list.html", context)
