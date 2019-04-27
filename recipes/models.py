from django.db import models

class Category(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class Recipe(models.Model):
    title = models.CharField(max_length=200)
    ingredients = models.TextField()
    directions = models.TextField()
    prep_time = models.CharField(max_length=100)
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.title

    def show_categories(self):
        return ', '.join([cat.title for cat in self.categories.all()])

    def print_ingredients(self):
        ing = self.ingredients.split(',')
        list = []
        for i in ing:
            list.append(i)
        return list
