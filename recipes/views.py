from decimal import Decimal
from fractions import Fraction

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DeleteView
from django_addanother.views import CreatePopupMixin

from .forms import (
    CategoryForm,
    CategoryFilterForm,
    ExcludeFoodForm,
    FoodFilterForm,
    ImageFormSet,
    IngredientFormSet,
    RecipeForm,
    RecipeSelectForm,
)
from .models import (
    Category,
    Food,
    RecipeImage,
    Ingredient,
    Recipe,
    get_converted_ingredients,
    get_recipe_list,
    get_search_results,
)

################################
# Category views
################################


def categories_overview(request):
    cats = Category.objects.all().order_by("title").all()
    categories = []
    for cat in cats:
        categories.append((cat, cat.get_recipes(request.user)))
    return render(
        request,
        "recipes/categories.html",
        {"categories": categories},
    )


def create_category(request):
    """
    For category creation using the category overview page
    """
    if request.method == "GET":
        form = CategoryForm()
        return render(request, "recipes/category_form.html", {"form": form})
    else:
        form = CategoryForm(request.POST)
        if not form.is_valid():
            return render(request, "recipes/category_form.html", {"form": form})
        category = form.save()
        return redirect("select-recipes", pk=category.pk)


def select_recipes(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "GET":
        form = RecipeSelectForm(user=request.user)
        return render(request, "recipes/select_recipes.html", {"form": form})
    else:
        form = RecipeSelectForm(request.user, request.POST)
        if not form.is_valid():
            return render(request, "recipes/select_recipes.html", {"form": form})
        selected_recipes = form.cleaned_data["recipes"]
        for rec in selected_recipes:
            rec.categories.add(category)
        return redirect("category-recipes", title=category.title)


class CategoryCreateView(CreatePopupMixin, LoginRequiredMixin, CreateView):
    """
    For category creation inside recipe creation
    """

    model = Category
    fields = ["title"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


def category_recipe_view(request, title):
    cat = get_object_or_404(Category, title=title)
    recipe_list = cat.get_recipes(request.user)
    page = request.GET.get("page")
    sortBy = request.GET.get("sortBy")

    if sortBy == "Name":
        recipe_list = recipe_list.order_by(Lower("title"))

    paginator = Paginator(recipe_list, 15)
    recipes = paginator.get_page(page)
    return render(
        request,
        "recipes/recipes_overview.html",
        {"recipes": recipes, "cat_title": cat.title, "sortBy": sortBy},
    )


################################
# Recipe views
################################
def prettyprint_amount(amount):
    # convert number to fraction
    frac = Fraction(amount)

    # number is simple int, so no pretty printing needed
    if frac.denominator == 1:
        return str(frac.numerator)

    # check if number is a neat fraction
    if frac.numerator < frac.denominator and frac.denominator <= 10:
        return str(frac).rstrip("0")

    # if the number is weirder, round it to a three decimal float
    return str(round(amount, 3)).rstrip("0")


def prettyprint_ingredient(ing):
    """
    Print ingredient in the form of: amount unit food_name (notes).
    For example: 100 g Flour (Type 405)
    """
    notes = f"({ing.get_notes()})" if len(ing.get_notes()) > 0 else ""
    return f"{prettyprint_amount(ing.get_amount())} {ing.get_unit()} {ing.get_food_name()} {notes}"


def prettyprint_servings(servings):
    serv = servings if (servings != int(servings)) else int(servings)
    return str(serv)


def recipe_overview(request):
    page = request.GET.get("page")
    sortBy = request.GET.get("sortBy")
    recipe_list = get_recipe_list(request.user)

    if sortBy == "Name":
        recipe_list = recipe_list.order_by(Lower("title"))

    paginator = Paginator(recipe_list, 15)
    recipes = paginator.get_page(page)
    return render(
        request,
        "recipes/recipes_overview.html",
        {"recipes": recipes, "sortBy": sortBy},
    )


def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    recipe.check_view_permissions(request.user)

    # if the number of servings was manually requested: recalculate the amounts of the ingredients accordingly
    if request.GET.get("number_servings"):
        servings = Decimal(request.GET.get("number_servings"))
        ingredients = [
            prettyprint_ingredient(ing)
            for ing in get_converted_ingredients(recipe, servings)
        ]
    # otherwise print the original ingredients
    else:
        ingredients = [prettyprint_ingredient(ing) for ing in recipe.get_ingredients()]
        servings = prettyprint_servings(recipe.get_servings())

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
    recipes = get_recipe_list(request.user)
    recipes = recipes.filter(author__username=username)
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
        request.user,
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
            "num_results": len(results),
            "category_form": category_form,
            "food_form": food_form,
            "exclude_food_form": exclude_food_form,
        },
    )


#######
# Image Gallery
def image_gallery(request):
    categories = Category.objects.all()
    cats_and_images = [(c, c.get_primary_images(request.user)) for c in categories]
    print(cats_and_images)
    return render(
        request, "recipes/image_gallery.html", {"cats_and_images": cats_and_images}
    )
