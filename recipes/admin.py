from django.contrib import admin
from .models import Food, Ingredient, Category, Recipe

admin.site.register(Food)
admin.site.register(Ingredient)
admin.site.register(Category)
admin.site.register(Recipe)
