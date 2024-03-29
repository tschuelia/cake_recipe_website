from django.urls import path

from . import views
from .views import RecipeDeleteView, CategoryCreateView

urlpatterns = [
    path("", views.recipe_overview, name="recipes-home"),
    path("advancedsearch/", views.advanced_search, name="advanced-search"),
    path("recipe/new", views.create_recipe, name="recipe-create"),
    path("recipe/<int:pk>", views.recipe_detail, name="recipe-detail"),
    path("recipe/<int:pk>/update", views.update_recipe, name="recipe-update"),
    path("recipe/<int:pk>/delete", RecipeDeleteView.as_view(), name="recipe-delete"),
    path("recipe/<int:pk>/addtocart", views.add_recipe_to_shopping_list, name="recipe-add-to-cart"),
    path("recipes/<str:username>", views.recipes_for_user, name="user-recipes"),
    path("categories", views.categories_overview, name="categories"),
    path(
        "categories/popup/new",
        CategoryCreateView.as_view(),
        name="category-create-popup",
    ),
    path("categories/new", views.create_category, name="category-create"),
    path(
        "categories/<int:pk>/selectrecipes", views.select_recipes, name="select-recipes"
    ),
    path("categories/<str:title>", views.category_recipe_view, name="category-recipes"),
    path("gallery", views.image_gallery, name="image-gallery"),
    # Shopping List
    path("shoppinglist", views.display_shopping_list, name="shopping-list"),
    path("shoppinglist/delete", views.delete_shopping_list, name="delete-shopping-list"),
    path("shoppinglist/<int:pk>/remove", views.remove_ingredients_from_shopping_list, name="remove-item-from-shopping-list"),
    # Ideas List
    path("ideas", views.display_ideas_list, name="ideas-list"),
    path("ideas/new", views.add_idea, name="add-idea"),
    path("ideas/<int:pk>/update", views.update_idea, name="update-idea"),
    path("ideas/<int:pk>/remove", views.delete_idea, name="delete-idea"),
]
