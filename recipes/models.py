from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from random import randint

from PIL import Image
from fractions import Fraction


##################################
# Category
##################################

class Category(models.Model):
    title = models.CharField(max_length=200, unique=True, verbose_name="Kategorie-Titel")

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
    name = models.CharField(max_length=200, unique=True, verbose_name="Lebensmittel")

    def __str__(self):
        return self.name

##################################
# Recipe
##################################

class Recipe(models.Model):
    title = models.CharField(max_length=200, verbose_name="Rezept-Titel")
    servings = models.DecimalField(max_digits=5, decimal_places=2, default=1, verbose_name="Portionen")
    directions = models.TextField(verbose_name="Zubereitung")
    prep_time = models.CharField(max_length=100, verbose_name="Zubereitungszeit")
    categories = models.ManyToManyField(Category, blank=True, verbose_name="Kategorien")
    image = models.ImageField(default='default.jpg', upload_to='recipe_pics', verbose_name="Bild")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, default=None, null=True)

    def __str__(self):
        return self.title

    # resize big images when uploading
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 1000 or img.width > 1000:
            output_size = (1000, 1000)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def get_categories(self):
        return self.categories.all().order_by('title')

    def get_ingredients(self):
        rec = get_object_or_404(Recipe, pk=self.pk)
        return Ingredient.objects.filter(recipe__pk__contains=rec.pk)

    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={'pk': self.pk})

    def get_servings(self):
        serv = self.servings if (self.servings != int(self.servings)) else int(self.servings)
        return str(serv)


##################################
# Ingredient
##################################
class Ingredient(models.Model):
    amount = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Anzahl")
    unit = models.CharField(max_length=20, blank=True, verbose_name="Einheit")
    food = models.ForeignKey(Food, on_delete=models.PROTECT, verbose_name="Lebensmittel")
    notes = models.TextField(blank=True, verbose_name="Anmerkungen")
    recipe = models.ForeignKey(Recipe, related_name="belongs_to", on_delete=models.CASCADE, null=True)

    def __str__(self):
        notes = f'({self.notes})' if len(self.notes) > 0 else ""
        return f'{str(Fraction(self.amount))}{self.unit} {self.food.name} {notes}'
