from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django_addanother.views import CreatePopupMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy


from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Recipe, Category, Ingredient
from .forms import RecipeForm
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

class CategoryRecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/category_recipes.html'
    context_object_name = 'recipes'
    paginate_by = 5

    def get_queryset(self):
        cat = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return Recipe.objects.filter(categories__pk__contains=cat.pk)

################################
# Recipe views
################################
class RecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/home.html'
    context_object_name = 'recipes'
    paginate_by = 5

class RecipeDetailView(DetailView):
    model = Recipe

class RecipeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recipe
    fields = ['title', 'ingredients', 'directions', 'prep_time', 'categories', 'image']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        recipe = self.get_object()
        if self.request.user == recipe.author:
            return True
        return False

class RecipeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recipe
    success_url = '/'

    def test_func(self):
        recipe = self.get_object()
        if self.request.user == recipe.author:
            return True
        return False


class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form = RecipeForm
    fields = ['title', 'directions', 'prep_time', 'categories', 'image']


    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


################################
# User views
################################
class UserRecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/user_recipes.html'
    context_object_name = 'recipes'
    paginate_by = 5

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
