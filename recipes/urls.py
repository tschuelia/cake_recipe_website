from django.urls import path
from .views import RecipeListView, RecipeDetailView, CategoryListView
from . import views


urlpatterns = [
    path('', RecipeListView.as_view(), name='recipes-home'),
    path('recipe/<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('about/', views.about, name='recipes-about'),
    path('categories/', CategoryListView.as_view(), name='recipes-categories')
]
