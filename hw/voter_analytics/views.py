# File: views.py
# Author: Declan Young (declanyg@bu.edu), 3/19/2026
# Description: views file for voter_analytics app

from django.shortcuts import render

# Create your views here.
def main(request):
    context = {
    }

    return render(request, "voter_analytics/index.html", context)