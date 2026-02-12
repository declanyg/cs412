# File: apps.py
# Author: Declan Young (declanyg@bu.edu), 3/05/2026
# Description: apps file to handle configuration for mini_insta app

from django.apps import AppConfig


class MiniInstaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hw.mini_insta"
