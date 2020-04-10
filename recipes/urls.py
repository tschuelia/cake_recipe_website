from django.urls import path
from .views import (
    RecipeListView,
    CategoryCreateView,
    RecipeDeleteView,
    RecipeSearchListView,
)
from . import views


urlpatterns = [
    path("", RecipeListView.as_view(), name="recipes-home"),
    path("recipe/<int:pk>", views.recipe_detail, name="recipe-detail"),
    path("recipe/new", views.create_recipe, name="recipe-create"),
    path("recipe/<int:pk>/update", views.update_recipe, name="recipe-update"),
    path("recipe/<int:pk>/delete", RecipeDeleteView.as_view(), name="recipe-delete"),
    path("categories", views.categories_overview, name="recipes-categories"),
    path("categories/new", CategoryCreateView.as_view(), name="category-create"),
    path("categories/<int:pk>", views.category_recipe_view, name="category-recipes"),
    path("user/<str:username>", views.recipes_for_user, name="user-recipes"),
    path("search", RecipeSearchListView.as_view(), name="search-results-recipe"),
]
