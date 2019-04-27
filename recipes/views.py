from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from .models import Recipe, Category

class RecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/home.html'
    context_object_name = 'recipes'


class CategoryListView(ListView):
    model = Category
    template_name = 'recipes/categories.html'
    context_object_name = 'categories'

class RecipeDetailView(DetailView):
    model = Recipe

def about(request):
    return render(request, 'recipes/about.html', {'title': 'About'})
