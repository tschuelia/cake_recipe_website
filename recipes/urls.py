from django.urls import path
from .views import (
    RecipeListView,
    RecipeDetailView,
    CategoryListView,
    CategoryCreateView,
    CategoryRecipeListView,
    RecipeCreateView,
    RecipeUpdateView,
    RecipeDeleteView,
    UserRecipeListView
)
from . import views


urlpatterns = [
    path('', RecipeListView.as_view(), name='recipes-home'),
    path('recipe/<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('recipe/new/', RecipeCreateView.as_view(), name='recipe-create'),
    path('recipe/<int:pk>/update/', RecipeUpdateView.as_view(), name='recipe-update'),
    path('recipe/<int:pk>/delete/', RecipeDeleteView.as_view(), name='recipe-delete'),
    path('about/', views.about, name='recipes-about'),
    path('categories/', CategoryListView.as_view(), name='recipes-categories'),
    path('categories/new/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/', CategoryRecipeListView.as_view(), name='category-recipes'),
    path('user/<str:username>/', UserRecipeListView.as_view(), name='user-recipes')
]
