from django.contrib import admin

from .models import Voter, Residential_Address

# Register your models here.
admin.site.register(Voter)
admin.site.register(Residential_Address)