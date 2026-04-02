# File: apps.py
# Author: Declan Young (declanyg@bu.edu), 4/1/2026
# Description: apps file to handle apps logic for dadjokes app

from django.apps import AppConfig


class DadjokesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hw.dadjokes"
