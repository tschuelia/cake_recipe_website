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


from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Recipe, Category, Ingredient, Food
from .forms import RecipeForm, IngredientFormSet
from random import randint

################################
# Category views
################################

class CategoryListView(ListView):
    model = Category
    template_name = 'recipes/categories.html'
    context_object_name = 'categories'
    ordering = ['title']

class CategoryCreateView(CreatePopupMixin, LoginRequiredMixin, CreateView):
    model = Category
    fields = ['title']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

def category_recipe_view(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    cat_title = cat.title
    recipe_list = Recipe.objects.filter(categories__pk__contains=cat.pk).order_by('title')
    paginator = Paginator(recipe_list, 5)
    page = request.GET.get('page')
    recipes = paginator.get_page(page)
    return render(request, 'recipes/category_recipes.html', {'recipes':recipes, 'cat_title':cat_title})


################################
# Recipe views
################################
class RecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/home.html'
    context_object_name = 'recipes'
    paginate_by = 5
    ordering = ['title']


def recipe_detail(request, pk):
    recipe = Recipe.objects.get(pk=pk)
    ingredients = recipe.get_ingredients
    servings = recipe.get_servings
    return render(request, 'recipes/recipe_detail.html', {'object': recipe, 'ingredients':ingredients, 'servings':servings})

def recipe_convert_servings(request, pk):
    recipe = Recipe.objects.get(pk=pk)
    ingredients = recipe.get_ingredients()
    servings_original = recipe.servings
    servings_desired = Decimal(request.GET.get('number_servings'))
    new_ingredients = []
    for ing in ingredients:
        amount_original = ing.amount
        amount_new = (amount_original / servings_original) * servings_desired
        new_ingredients.append(Ingredient(amount=amount_new, unit=ing.unit, food=ing.food, notes=ing.notes, recipe=None))
    return render(request, 'recipes/recipe_detail.html', {'object': recipe, 'ingredients': new_ingredients, 'servings':servings_desired})

@login_required
def update_recipe(request, pk):
    recipe = Recipe.objects.get(pk=pk)
    if not request.user == recipe.author:
        raise PermissionDenied
    if request.method == 'GET':
        # Anzeigen
        recipe_form = RecipeForm(instance=recipe)
        ingredients_formset = IngredientFormSet(instance=recipe)
        return render(request, 'recipes/recipe_form.html', {
            'form': recipe_form,
            'ingredients': ingredients_formset,
        })
    else: # method == 'POST'
        # Abgeschicktes Formular verarbeiten
        recipe_form = RecipeForm(request.POST, request.FILES, instance=recipe)
        ingredients_formset = IngredientFormSet(request.POST, instance=recipe)
        if not recipe_form.is_valid():
            return render(request, 'recipes/recipe_form.html', {
                'form': recipe_form,
                'ingredients': ingredients_formset,
            })
        if not ingredients_formset.is_valid():
            return render(request, 'recipes/recipe_form.html', {
                'form': recipe_form,
                'ingredients': ingredients_formset,
            })
        recipe_form.instance.author = request.user
        recipe_obj = recipe_form.save()

        ingredients_formset.instance = recipe_obj
        ingredients_formset.save()

        return redirect(recipe_obj)


class RecipeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recipe
    success_url = '/'

    def test_func(self):
        recipe = self.get_object()
        if self.request.user == recipe.author:
            return True
        return False


@login_required
def create_recipe(request):
    if request.method == 'GET':
        # Anzeigen
        recipe_form = RecipeForm()
        ingredients_formset = IngredientFormSet()
        return render(request, 'recipes/recipe_form.html', {
            'form': recipe_form,
            'ingredients': ingredients_formset,
        })
    else: # method == 'POST'
        # Abgeschicktes Formular verarbeiten
        recipe_form = RecipeForm(request.POST, request.FILES)
        ingredients_formset = IngredientFormSet(request.POST)
        if not recipe_form.is_valid():
            return render(request, 'recipes/recipe_form.html', {
                'form': recipe_form,
                'ingredients': ingredients_formset,
            })
        if not ingredients_formset.is_valid():
            return render(request, 'recipes/recipe_form.html', {
                'form': recipe_form,
                'ingredients': ingredients_formset,
            })
        recipe_form.instance.author = request.user
        recipe_obj = recipe_form.save()

        ingredients_formset.instance = recipe_obj
        ingredients_formset.save()

        return redirect(recipe_obj)


################################
# User views
################################
class UserRecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/user_recipes.html'
    context_object_name = 'recipes'
    paginate_by = 5
    ordering = ['title']

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Recipe.objects.filter(author=user)

def about(request):
    return render(request, 'recipes/about.html', {'title': 'About'})

####################
class RecipeSearchListView(RecipeListView):
    """
    Display a Recipe List page filtered by the search query.
    """
    model = Recipe
    template_name = 'recipes/search_results_recipes.html'
    context_object_name = 'recipes'
    paginate_by = 5

    def get_queryset(self):
        result = super(RecipeSearchListView, self).get_queryset()

        query = self.request.GET.get('q')
        if query:
            result = result.filter(title__icontains=query)
        return result
