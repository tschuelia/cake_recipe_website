from django.db import models
from PIL import Image

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
    image = models.ImageField(default='default.jpg', upload_to='recipe_pics')

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

    def show_categories(self):
        return ', '.join([cat.title for cat in self.categories.all()])

    def print_ingredients(self):
        ing = self.ingredients.split(',')
        list = []
        for i in ing:
            list.append(i)
        return list
