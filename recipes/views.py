from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView
from django_addanother.views import CreatePopupMixin

from .forms import (
    CategoryFilterForm,
    ExcludeFoodForm,
    FoodFilterForm,
    ImageFormSet,
    IngredientFormSet,
    RecipeForm,
)
from .models import (
    Category,
    Food,
    Image,
    Ingredient,
    Recipe,
    get_converted_ingredients,
    get_search_results,
)

################################
# Category views
################################


def categories_overview(request):
    cats = Category.objects.all().order_by("title").all()
    categories = []
    for cat in cats:
        categories.append((cat, cat.random_recipe()))
    return render(request, "recipes/categories.html", {"categories": categories})


class CategoryCreateView(CreatePopupMixin, LoginRequiredMixin, CreateView):
    model = Category
    fields = ["title"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


def category_recipe_view(request, title):
    cat = get_object_or_404(Category, title=title)
    recipe_list = cat.get_recipes()

    paginator = Paginator(recipe_list, 15)
    page = request.GET.get("page")
    recipes = paginator.get_page(page)
    return render(
        request,
        "recipes/recipes_overview.html",
        {"recipes": recipes, "cat_title": cat.title},
    )


################################
# Recipe views
################################
def recipe_overview(request):
    recipe_list = Recipe.objects.all().order_by("title")
    paginator = Paginator(recipe_list, 15)
    page = request.GET.get("page")
    recipes = paginator.get_page(page)
    return render(request, "recipes/recipes_overview.html", {"recipes": recipes},)


def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.GET.get("number_servings"):
        servings = Decimal(request.GET.get("number_servings"))
        ingredients = get_converted_ingredients(recipe, servings)

    else:
        ingredients = recipe.get_ingredients
        servings = recipe.get_servings
    return render(
        request,
        "recipes/recipe_detail.html",
        {"recipe": recipe, "ingredients": ingredients, "servings": servings},
    )


@login_required
def create_recipe(request):
    if request.method == "GET":
        return display_recipe_form(request)
    else:
        return process_recipe_form(request)


@login_required
def update_recipe(request, pk):
    recipe = Recipe.objects.get(pk=pk)
    if not request.user == recipe.author:
        raise PermissionDenied
    if request.method == "GET":
        return display_recipe_form(request, recipe)
    else:
        return process_recipe_form(request, recipe)


def display_recipe_form(request, recipe=None):
    recipe_form = RecipeForm(instance=recipe)
    image_form = ImageFormSet(instance=recipe)
    ingredients_formset = IngredientFormSet(instance=recipe)
    return render(
        request,
        "recipes/recipe_form.html",
        {
            "form": recipe_form,
            "images": image_form,
            "ingredients": ingredients_formset,
        },
    )


def process_recipe_form(request, recipe=None):
    recipe_form = RecipeForm(request.POST, instance=recipe)
    image_formset = ImageFormSet(request.POST, request.FILES, instance=recipe)
    ingredients_formset = IngredientFormSet(request.POST, instance=recipe)
    if (
        (not recipe_form.is_valid())
        or (not image_formset.is_valid())
        or (not ingredients_formset.is_valid())
    ):
        return render(
            request,
            "recipes/recipe_form.html",
            {
                "form": recipe_form,
                "images": image_formset,
                "ingredients": ingredients_formset,
            },
        )
    recipe_form.instance.author = request.user
    recipe_obj = recipe_form.save()

    image_formset.instance = recipe_obj
    image_formset.save()

    ingredients_formset.instance = recipe_obj
    ingredients_formset.save()

    return redirect(recipe_obj)


class RecipeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recipe
    success_url = "/"

    def test_func(self):
        recipe = self.get_object()
        if self.request.user == recipe.author:
            return True
        return False


################################
# User views
################################
def recipes_for_user(request, username):
    recipes = Recipe.objects.filter(author__username=username)
    return render(
        request,
        "recipes/recipes_overview.html",
        {"recipes": recipes, "username": username},
    )


################################
# Advanced search
################################
def advanced_search(request):
    category_form = CategoryFilterForm(request.GET)
    food_form = FoodFilterForm(request.GET)
    exclude_food_form = ExcludeFoodForm(request.GET)
    _and = "_and" in request.GET
    results = get_search_results(
        request.GET.get("q"),
        request.GET.getlist("c"),
        request.GET.getlist("f"),
        request.GET.getlist("ex"),
        _and,
    )

    return render(
        request,
        "recipes/advanced_search.html",
        {
            "search_term": request.GET.get("q"),
            "search_results": results,
            "category_form": category_form,
            "food_form": food_form,
            "exclude_food_form": exclude_food_form,
        },
    )
