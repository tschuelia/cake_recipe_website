from django import forms
from django.urls import reverse_lazy
from django_addanother.widgets import AddAnotherWidgetWrapper
from .models import Recipe, Ingredient




class RecipeForm(forms.ModelForm):
    class Meta:
          model = Recipe
          exclude = ()
          widgets = {
                'categories': AddAnotherWidgetWrapper(
                    forms.SelectMultiple,
                    reverse_lazy('category-create'),
                )
            }
