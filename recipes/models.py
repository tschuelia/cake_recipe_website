from decimal import Decimal
from random import randint

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from model_utils.models import TimeStampedModel
from watson import search as watson

from .utils import get_image_size


class Category(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name="Name")

    def __str__(self):
        return self.title

    def get_recipes(self, user):
        recipes = self.recipe_set.order_by("-modified")
        return filter_recipe_list(user, recipes)

    def get_absolute_url(self):
        return reverse("category-recipes", kwargs={"title": self.title})

    def random_recipe(self, user):
        """
        Returns a random recipe of the list of recipes that are accessible for this user.
        """
        return self.get_recipes(user).order_by("?").first()

    def get_primary_images(self, user):
        recipes = self.recipe_set.order_by("-modified")
        recipes = filter_recipe_list(user, recipes, filter_empty=False)
        return [rec.get_primary_image() for rec in recipes if rec.get_primary_image()]


class Food(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Lebensmittel")

    def __str__(self):
        return self.name


class Recipe(TimeStampedModel):
    title = models.CharField(max_length=255, verbose_name="Titel")
    introduction = models.TextField(verbose_name="Einleitung", blank=True)
    servings = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1,
        verbose_name="Portionen",
        blank=True,
        null=True,
    )
    directions = models.TextField(verbose_name="Zubereitung", blank=True)
    prep_time = models.CharField(
        max_length=100, verbose_name="Zubereitungszeit", blank=True
    )
    categories = models.ManyToManyField(Category, blank=True, verbose_name="Kategorien")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, default=None, null=True)
    notes = models.TextField(verbose_name="Notizen", blank=True)
    secret_notes = models.TextField(verbose_name="Geheime Notizen", blank=True)
    related_recipes = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        verbose_name="zugehörige Rezepte",
    )
    public = models.BooleanField(default=False, verbose_name="für alle sichtbar")

    def __str__(self):
        return self.title

    def get_categories(self):
        return self.categories.all().order_by("title")

    def get_ingredients(self):
        return self.belongs_to.all()

    def get_absolute_url(self):
        return reverse("recipe-detail", kwargs={"pk": self.pk})

    def get_servings(self):
        return self.servings

    def get_images(self):
        return self.image_of.all().order_by("-is_primary")

    def get_primary_image(self):
        return self.image_of.filter(is_primary=True).first()

    def check_view_permissions(self, user):
        # admins may see everything
        if user.is_superuser:
            return

        # users that are not logged in may only see public recipes
        if not (user.is_authenticated or self.public):
            raise PermissionDenied

        # logged in users may only see their own and public recipes
        if not (self.author == user or self.public):
            raise PermissionDenied


class Ingredient(models.Model):
    amount = models.DecimalField(max_digits=6, decimal_places=3, verbose_name="Anzahl")
    unit = models.CharField(max_length=20, blank=True, verbose_name="Einheit")
    food = models.ForeignKey(Food, on_delete=models.PROTECT, verbose_name="Zutat")
    notes = models.TextField(blank=True, verbose_name="Notiz")
    recipe = models.ForeignKey(
        Recipe, related_name="belongs_to", on_delete=models.CASCADE, null=False
    )

    def __str__(self):
        return self.food.name

    def get_amount(self):
        return self.amount

    def get_unit(self):
        return self.unit

    def get_food_name(self):
        return self.food.name

    def get_notes(self):
        return self.notes


class RecipeImage(models.Model):
    image = models.ImageField(
        default="default.jpg", upload_to="recipe_pics", verbose_name="Bilder"
    )
    recipe = models.ForeignKey(
        Recipe, related_name="image_of", on_delete=models.CASCADE, null=True
    )
    is_primary = models.BooleanField(default=False, verbose_name="Titelbild")

    def __str__(self):
        return self.recipe.title

    def get_url(self):
        return self.image.url

    def get_height(self):
        height, _ = get_image_size(self.image)
        return height

    def get_width(self):
        _, width = get_image_size(self.image)
        return width


def get_recipe_list(user):
    """
    Get the list of recipes accessible to the given user, ordered by least recently modified.

    If the given user is no registered and logged in user, only recipes marked as publicly available will be returned.
    If the given user is logged in, all recipes that are either publicly available or belong to the user will be returned.
    If the given user is a superuser, all recipes will be returned.
    """
    recipes = Recipe.objects.all().order_by("-modified")
    return filter_recipe_list(user, recipes)


def get_modifiable_recipe_list(user):
    return Recipe.objects.filter(author=user).order_by("title")


def get_search_results(
    user, search_term, categories, foods, excluded_foods, contains_all=False
):
    """
    Filter list of recipes according to the search. Only the recipes accessible to the given users will be searched.
    Returns a list of recipes ordered by title.

    search_term: String. Recipe.title, Recipe.instructions, Recipe.notes will be searched for this term
    categories: List of Category Objects. Only recipes of these categories will be returned. If empty all categories are searched.
    foods: List of Food Objects. Only recipes containing these foods as ingredients will be returned. If empty all foods are considered.
    excluded_foods: List of Food Objects. Only recipes NOT containing these foods as ingredients will be returned.
    contains_all: If True, only recipes containing all Food Objects given in 'food' as ingredient will be returned.
                  If False, recipes containing any of the foods will be returned.
    """
    # get the list of recipes accessible to the given user
    recipes = get_recipe_list(user)

    # if a search term is given: use watson to search the recipe titles, instructions and notes for the given term
    if search_term:
        results = watson.search(search_term)
        pks = [r.object_id_int for r in results]
        recipes = recipes.filter(pk__in=pks)

    # if category objects are given: keep only recipes of these categories
    if categories:
        recipes = recipes.filter(categories__in=categories)

    # if food objects are given: filter recipes according to contains_all
    if foods:
        # if contains_all is set to True: keep only recipes containing all given foods
        if contains_all:
            for food in foods:
                ingredients = Ingredient.objects.filter(food=food)
                recipe_pks = ingredients.values_list("recipe", flat=True)
                recipes = recipes.filter(pk__in=recipe_pks)
        # if contains_all is set to False: keep only recipes containing any of the given foods
        else:
            ingredients = Ingredient.objects.filter(food__in=foods)
            recipe_pks = ingredients.values_list("recipe", flat=True)
            recipes = recipes.filter(pk__in=recipe_pks)

    # if exclude food objects are given: keep only recipes containing none of the given foods
    if excluded_foods:
        ingredients = Ingredient.objects.filter(food__in=excluded_foods)
        recipe_pks = ingredients.values_list("recipe", flat=True)
        recipes = recipes.exclude(pk__in=recipe_pks)

    return recipes.order_by("title")


def get_converted_ingredients(recipe, new_servings):
    """
    Convert the amounts of ingredients for the given recipe according to the new number of servings.
    """
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


def filter_recipe_list(user, recipes, filter_empty=True):
    """
    If the given user is a superuser, all recipes will be returned.
    If the given user is logged in, all recipes that are either publicly available or belong to the user will be returned.
    If the given user is no registered and logged in user, only recipes marked as publicly available will be returned.

    The recipes are further filtered by whether they are a full recipe or not.
    """
    if user.is_superuser:
        recipes = recipes.all()
    elif user.is_authenticated:
        recipes = recipes.filter(Q(public=True) | Q(author=user))
    else:
        recipes = recipes.filter(public=True)

    if filter_empty:
        # full recipe is defined by having
        # - introduction
        # - directions
        # - servings
        has_intro = ~Q(introduction="")
        has_dir = ~Q(directions="")
        has_serv = ~Q(servings=None)
        recipes = recipes.filter(has_intro & has_dir & has_serv)
    return recipes