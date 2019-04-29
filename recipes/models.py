from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

from PIL import Image

class Category(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('recipes-categories', kwargs={'pk': self.pk})


class Recipe(models.Model):
    title = models.CharField(max_length=200)
    ingredients = models.TextField()
    directions = models.TextField()
    prep_time = models.CharField(max_length=100)
    categories = models.ManyToManyField(Category, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='recipe_pics')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

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

    def print_ingredients(self):
        ing = self.ingredients.split(',')
        list = []
        for i in ing:
            list.append(i)
        return list

    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={'pk': self.pk})
