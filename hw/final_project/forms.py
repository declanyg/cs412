# File: forms.py
# Author: Declan Young (declanyg@bu.edu), 26/04/2026
# Description: forms file to handle form definitions for final_project app

from django import forms
from .models import *

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['quantity', 'special_instructions']


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, f"{i}") for i in range(5, 0, -1)],
        widget=forms.RadioSelect,
        label='Rating',
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Share your thoughts...',
            }),
        }
        labels = {
            'comment': 'Your review',
        }
