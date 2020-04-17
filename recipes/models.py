from fractions import Fraction
from random import randint

from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from watson import search as watson


class Category(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name="Name")

    def __str__(self):
        return self.title

    def get_recipes(self):
        return self.recipe_set.all()

    def get_absolute_url(self):
        return reverse("category-recipes", kwargs={"title": self.title})

    def random_recipe(self):
        cat = get_object_or_404(Category, pk=self.pk)
        return (
            Recipe.objects.filter(categories__pk__contains=cat.pk).order_by("?").first()
        )


class Food(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Lebensmittel")

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=255, verbose_name="Titel")
    introduction = models.TextField(verbose_name="Einleitung", null=True)
    servings = models.DecimalField(
        max_digits=5, decimal_places=2, default=1, verbose_name="Portionen"
    )
    directions = models.TextField(verbose_name="Zubereitung")
    prep_time = models.CharField(max_length=100, verbose_name="Zubereitungszeit")
    categories = models.ManyToManyField(Category, blank=True, verbose_name="Kategorien")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, default=None, null=True)
    notes = models.TextField(verbose_name="Notizen", blank=True)
    related_recipes = models.ManyToManyField(
        "self", blank=True, symmetrical=False, verbose_name="zugehörige Rezepte",
    )

    def __str__(self):
        return self.title

    def get_categories(self):
        return self.categories.all().order_by("title")

    def get_ingredients(self):
        return Ingredient.objects.filter(recipe__pk__contains=self.pk)

    def get_absolute_url(self):
        return reverse("recipe-detail", kwargs={"pk": self.pk})

    def get_servings(self):
        serv = (
            self.servings
            if (self.servings != int(self.servings))
            else int(self.servings)
        )
        return str(serv)

    def get_images(self):
        return Image.objects.filter(recipe__pk__contains=self.pk).order_by(
            "-is_primary"
        )

    def get_primary_image(self):
        return Image.objects.filter(
            recipe__pk__contains=self.pk, is_primary=True
        ).first()


class Ingredient(models.Model):
    amount = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Anzahl")
    unit = models.CharField(max_length=20, blank=True, verbose_name="Einheit")
    food = models.ForeignKey(Food, on_delete=models.PROTECT, verbose_name="Zutat")
    notes = models.TextField(blank=True, verbose_name="Notiz")
    recipe = models.ForeignKey(
        Recipe, related_name="belongs_to", on_delete=models.CASCADE, null=False
    )

    def __str__(self):
        notes = f"({self.notes})" if len(self.notes) > 0 else ""
        return f"{str(Fraction(self.amount))}{self.unit} {self.food.name} {notes}"


class Image(models.Model):
    image = models.ImageField(
        default="default.jpg", upload_to="recipe_pics", verbose_name="Bilder"
    )
    recipe = models.ForeignKey(
        Recipe, related_name="image_of", on_delete=models.CASCADE, null=True
    )
    is_primary = models.BooleanField(default=False, verbose_name="Titelbild")

    def __str__(self):
        return self.image.name

    def get_url(self):
        return self.image.url

    """# resize big images when uploading
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 1000 or img.width > 1000:
            output_size = (1000, 1000)
            img.thumbnail(output_size)
            img.save(self.image.path)"""


def get_search_results(
    search_term, categories, foods, excluded_foods, contains_all=False
):
    recipes = Recipe.objects.all()
    if search_term:
        results = watson.search(search_term)
        pks = [r.object_id_int for r in results]
        recipes = recipes.filter(pk__in=pks)

    if categories:
        recipes = recipes.filter(categories__in=categories)

    if foods:
        if contains_all:
            for food in foods:
                ingredients = Ingredient.objects.filter(food=food)
                recipe_pks = ingredients.values_list("recipe", flat=True)
                recipes = recipes.filter(pk__in=recipe_pks)
        else:
            ingredients = Ingredient.objects.filter(food__in=foods)
            recipe_pks = ingredients.values_list("recipe", flat=True)
            recipes = recipes.filter(pk__in=recipe_pks)

    if excluded_foods:
        ingredients = Ingredient.objects.filter(food__in=excluded_foods)
        recipe_pks = ingredients.values_list("recipe", flat=True)
        recipes = recipes.exclude(pk__in=recipe_pks)

    return recipes.order_by("title")


def get_converted_ingredients(recipe, new_servings):
    ingredients = recipe.get_ingredients()
    servings_original = recipe.servings
    new_ingredients = []
    for ing in ingredients:
        amount_original = ing.amount
        amount_new = (ing.amount / recipe.servings) * new_servings
        new_ingredients.append(
            Ingredient(
                amount=amount_new,
                unit=ing.unit,
                food=ing.food,
                notes=ing.notes,
                recipe=None,
            )
        )
    return new_ingredients
