from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from random import randint

from PIL import Image


##################################
# Category
##################################

class Category(models.Model):
    title = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category-recipes', kwargs={'pk': self.pk})

    def random_recipe(self):
        cat = get_object_or_404(Category, pk=self.pk)
        return Recipe.objects.filter(categories__pk__contains=cat.pk).order_by('?').first()

##################################
# Food
##################################
class Food(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


##################################
# Ingredient
##################################
class Ingredient(models.Model):
    food = models.ForeignKey(Food, on_delete=models.PROTECT)
    unit = models.CharField(max_length=20, blank=True)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    notes = models.TextField(blank=True)

    def __str__(self):
        am = self.amount if self.amount < 0 else int(self.amount)
        return str(am) + self.unit + " " + self.food.name


##################################
# Recipe
##################################

class Recipe(models.Model):
    title = models.CharField(max_length=200)
    ingredients = models.ManyToManyField(Ingredient, blank=True)
    directions = models.TextField()
    prep_time = models.CharField(max_length=100)
    categories = models.ManyToManyField(Category, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='recipe_pics')
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.title

    # resize big images when uploading
    def save(self):
        super().save()
        img = Image.open(self.image.path)
        if img.height > 1000 or img.width > 1000:
            output_size = (1000, 1000)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def get_categories(self):
        return self.categories.all()

    def get_ingredients(self):
        return self.ingredients.all()

    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={'pk': self.pk})
