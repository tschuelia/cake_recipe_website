from django.contrib import admin
from .models import Food, Ingredient, Category, Recipe, RecipeImage, ShoppingList, ShoppingListRecipe

admin.site.register(Food)
admin.site.register(Ingredient)
admin.site.register(Category)
admin.site.register(Recipe)
admin.site.register(RecipeImage)
admin.site.register(ShoppingList)
admin.site.register(ShoppingListRecipe)

