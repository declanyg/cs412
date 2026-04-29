# File: forms.py
# Author: Declan Young (declanyg@bu.edu), 26/04/2026
# Description: forms file to handle form definitions for final_project app

from django import forms
from .models import *

class OrderItemForm(forms.ModelForm):
    """Form for editing an OrderItem's quantity and special instructions.
    """
    class Meta:
        """Specify the model and fields to include in the form.
        """
        model = OrderItem
        fields = ['quantity', 'special_instructions']


class MenuItemForm(forms.ModelForm):
    """Form for creating/editing a MenuItem.
    """
    class Meta:
        """Specify the model and fields to include in the form.
        """
        model = MenuItem
        fields = ['name', 'description', 'price', 'category', 'available']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Optional — describe the dish.',
            }),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'category': forms.TextInput(attrs={
                'placeholder': 'e.g. Mains, Drinks, Desserts',
            }),
        }


class ReviewForm(forms.ModelForm):
    """Form for creating/editing a Review.
    """
    rating = forms.ChoiceField(
        choices=[(i, f"{i}") for i in range(5, 0, -1)],
        widget=forms.RadioSelect,
        label='Rating',
    )

    class Meta:
        """Specify the model and fields to include in the form.
        """
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
