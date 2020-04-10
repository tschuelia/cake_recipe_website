from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django_addanother.views import CreatePopupMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator

from decimal import Decimal
from random import randint

from django.views.generic import ListView, CreateView, DeleteView

from .models import Recipe, Category, Ingredient, Image, Food
from .forms import RecipeForm, IngredientFormSet, ImageFormSet

################################
# Category views
################################


def categories_overview(request):
    cats = Category.objects.all().order_by("title").all()
    categories = []
    for cat in cats:
        print(cat)
        categories.append((cat, cat.random_recipe()))
    return render(request, "recipes/categories.html", {"categories": categories})


class CategoryCreateView(CreatePopupMixin, LoginRequiredMixin, CreateView):
    model = Category
    fields = ["title"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


def category_recipe_view(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    cat_title = cat.title
    recipe_list = cat.get_recipes()

    paginator = Paginator(recipe_list, 5)
    page = request.GET.get("page")
    recipes = paginator.get_page(page)
    return render(
        request,
        "recipes/recipes_overview.html",
        {"recipes": recipes, "cat_title": cat_title},
    )


################################
# Recipe views
################################
class RecipeListView(ListView):
    model = Recipe
    template_name = "recipes/recipes_overview.html"
    context_object_name = "recipes"
    paginate_by = 12
    ordering = ["title"]


def recipe_detail(request, pk):
    recipe = Recipe.objects.get(pk=pk)
    ingredients = recipe.get_ingredients
    images = recipe.get_images
    servings = recipe.get_servings
    return render(
        request,
        "recipes/recipe_detail.html",
        {
            "recipe": recipe,
            "images": images,
            "ingredients": ingredients,
            "servings": servings,
        },
    )


def recipe_convert_servings(request, pk):
    recipe = Recipe.objects.get(pk=pk)
    ingredients = recipe.get_ingredients()
    images = recipe.get_images
    servings_original = recipe.servings
    servings_desired = Decimal(request.GET.get("number_servings"))
    new_ingredients = []
    for ing in ingredients:
        amount_original = ing.amount
        amount_new = (amount_original / servings_original) * servings_desired
        new_ingredients.append(
            Ingredient(
                amount=amount_new,
                unit=ing.unit,
                food=ing.food,
                notes=ing.notes,
                recipe=None,
            )
        )
    return render(
        request,
        "recipes/recipe_detail.html",
        {
            "object": recipe,
            "images": images,
            "ingredients": new_ingredients,
            "servings": servings_desired,
        },
    )


@login_required
def create_recipe(request):
    if request.method == "GET":
        return display_recipe_form(request)
    else:  # method == 'POST'
        return process_recipe_form(request)


@login_required
def update_recipe(request, pk):
    recipe = Recipe.objects.get(pk=pk)
    if not request.user == recipe.author:
        raise PermissionDenied
    if request.method == "GET":
        return display_recipe_form(request, recipe)
    else:  # method == 'POST'
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


####################
class RecipeSearchListView(RecipeListView):
    """
    Display a Recipe List page filtered by the search query.
    """

    model = Recipe
    template_name = "recipes/recipes_overview.html"
    context_object_name = "recipes"
    paginate_by = 12

    def get_queryset(self):
        result = super(RecipeSearchListView, self).get_queryset()

        query = self.request.GET.get("q")
        if query:
            result = result.filter(title__icontains=query)
        return result
