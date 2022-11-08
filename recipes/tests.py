import unittest

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.test import Client, TestCase

from .forms import IngredientForm, IngredientFormSet
from .models import Category, Food, Ingredient, Recipe


class TestRecipeModel(TestCase):
    def setUp(self):
        auth_user = User.objects.create_user(
            "auth_user", "auth_user@test.com", "auth_userPW"
        )
        other_user = User.objects.create_user(
            "other_user", "other_user@test.com", "other_userPW"
        )

        Recipe.objects.create(title="auth_user_recipe", author=auth_user)

        Recipe.objects.create(title="other_user_recipe", author=other_user)

        Recipe.objects.create(
            title="other_user_recipe_public", author=other_user, public=True
        )

    def test_check_recipe_view_permissions_admin(self):
        """
        The admin user should be able to view all available recipes.
        """
        recipes = Recipe.objects.all()
        admin = User.objects.create_superuser("admin", "admin@test.com", "adminPW")
        for rec in recipes:
            try:
                rec.check_view_permissions(admin)
            except PermissionDenied:
                self.fail("Admin should be able to view all recipes")

    def test_check_recipe_view_permissions_auth_user(self):
        """The auth_user should be able to access
            - his own recipe
            - the public recipe of other_user
            and should NOT be able to access
            - the private recipe of other_user
        """
        auth_user = User.objects.get(username="auth_user")
        auth_user_rec = Recipe.objects.get(title="auth_user_recipe")
        try:
            auth_user_rec.check_view_permissions(auth_user)
        except PermissionDenied:
            self.fail("auth_user should be able to view his own recipe")

        other_user_public_res = Recipe.objects.get(title="other_user_recipe_public")
        try:
            other_user_public_res.check_view_permissions(auth_user)
        except PermissionDenied:
            self.fail("auth_user should be able to view public recipes")

        other_user_private_res = Recipe.objects.get(title="other_user_recipe")
        with self.assertRaises(PermissionDenied):
            other_user_private_res.check_view_permissions(auth_user)


"""class Test(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_recipe_view(self):
        cat1 = Category.objects.create(title="Cat1")
        user = User.objects.create_user("testUser", "test@test.com", "testPassword")
        self.client.login(username="testUser", password="testPassword")
        re = self.client.post(
            "/recipe/new/",
            {
                "title": "Rec1",
                "servings": ["1.00"],
                "belongs_to-TOTAL_FORMS": "1",
                "belongs_to-INITIAL_FORMS": "0",
                "belongs_to-MIN_NUM_FORMS": "0",
                "belongs_to-MAX_NUM_FORMS": "1000",
                "belongs_to-0-id": "",
                "belongs_to-0-recipe": "",
                "belongs_to-0-amount": "100",
                "belongs_to-0-unit": "TestUnit",
                "belongs_to-0-food_name": "TestFood",
                "belongs_to-0-notes": "TestNote",
                "belongs_to-0-DELETE": "",
                "directions": "bake",
                "prep_time": "1h",
                "categories": cat1.pk,
            },
        )
        recipe = Recipe.objects.get(title="Rec1")
        self.assertEqual(recipe.directions, "bake")
        self.assertEqual(recipe.prep_time, "1h")
        self.assertEqual([cat.pk for cat in recipe.get_categories()], [cat1.pk])
        self.assertEqual(recipe.author, user)
        self.assertEqual(recipe.image, "default.jpg")

        self.assertEqual(Food.objects.all().count(), 1)
        food = Food.objects.get(name="TestFood")
        self.assertEqual(food.name, "TestFood")

        self.assertEqual(Ingredient.objects.all().count(), 1)
        ing = Ingredient.objects.get(amount=100, unit="TestUnit")
        self.assertEqual(ing.amount, 100)
        self.assertEqual(ing.unit, "TestUnit")
        self.assertEqual(ing.notes, "TestNote")
        self.assertEqual(ing.food, food)

        url = f"/recipe/{recipe.pk}/"
        self.assertRedirects(re, url)

    def create_dummy_data(self):
        self.user1 = User.objects.create_user(
            "testUser", "test@test.com", "testPassword"
        )
        self.user2 = User.objects.create_user(
            "testUser2", "test2@test.com", "testPassword2"
        )

        self.cat1 = Category.objects.create(title="Cat1")
        self.cat2 = Category.objects.create(title="Cat2")

        self.food1 = Food.objects.create(name="Food1")
        self.food2 = Food.objects.create(name="Food2")
        self.food3 = Food.objects.create(name="Food3")

        self.rec1 = Recipe.objects.create(
            title="Rec1",
            directions="Dir1",
            prep_time="1",
            author=self.user1,
            servings=1,
        )
        self.rec2 = Recipe.objects.create(
            title="Rec2",
            directions="Dir2",
            prep_time="2",
            author=self.user2,
            servings=2,
        )
        self.rec1.categories.add(self.cat1)
        self.rec2.categories.add(self.cat2)

        self.ing1 = Ingredient.objects.create(
            amount=1, unit="testUnit1", food=self.food1, notes="", recipe=self.rec1
        )
        self.ing2 = Ingredient.objects.create(
            amount=2,
            unit="testUnit2",
            food=self.food2,
            notes="TestNote",
            recipe=self.rec2,
        )

    def test_ingredient_creation_on_update(self):
        self.create_dummy_data()
        self.client.login(username="testUser", password="testPassword")
        re = self.client.post(
            f"/recipe/{self.rec1.pk}/update/",
            {
                "title": self.rec1.title,
                "prep_time": self.rec1.prep_time,
                "servings": self.rec1.servings,
                "belongs_to-TOTAL_FORMS": "2",
                "belongs_to-INITIAL_FORMS": "1",
                "belongs_to-MIN_NUM_FORMS": "0",
                "belongs_to-MAX_NUM_FORMS": "1000",
                "belongs_to-0-id": self.ing1.pk,
                "belongs_to-0-recipe": self.rec1.pk,
                "belongs_to-0-amount": self.ing1.amount,
                "belongs_to-0-unit": self.ing1.unit,
                "belongs_to-0-food_name": self.ing1.food.name,
                "belongs_to-0-notes": "",
                "belongs_to-0-DELETE": "",
                "belongs_to-1-id": "",
                "belongs_to-1-recipe": self.rec1.pk,
                "belongs_to-1-amount": "3",
                "belongs_to-1-unit": "testUnit3",
                "belongs_to-1-food_name": "Food3",
                "belongs_to-1-notes": "",
                "belongs_to-1-DELETE": "",
                "directions": self.rec1.directions,
                "categories": self.cat1.pk,
                "image": "",
            },
        )
        # add only one new ingredient to recipe with one ingredient set -> 2 ingredients
        self.assertEqual(Ingredient.objects.filter(recipe=self.rec1.pk).count(), 2)
        self.assertEqual(Food.objects.all().count(), 3)

    def test_ingredient_deletion_on_update(self):
        self.create_dummy_data()
        ing3 = Ingredient.objects.create(
            amount=3,
            unit="testUnit3",
            food=self.food3,
            notes="TestNote",
            recipe=self.rec1,
        )
        self.assertEqual(Ingredient.objects.filter(recipe=self.rec1.pk).count(), 2)
        self.client.login(username="testUser", password="testPassword")
        re = self.client.post(
            f"/recipe/{self.rec1.pk}/update/",
            {
                "title": self.rec1.title,
                "prep_time": self.rec1.prep_time,
                "servings": self.rec1.servings,
                "belongs_to-TOTAL_FORMS": "3",
                "belongs_to-INITIAL_FORMS": "2",
                "belongs_to-MIN_NUM_FORMS": "0",
                "belongs_to-MAX_NUM_FORMS": "1000",
                "belongs_to-0-id": self.ing1.pk,
                "belongs_to-0-recipe": self.rec1.pk,
                "belongs_to-0-amount": self.ing1.amount,
                "belongs_to-0-unit": self.ing1.unit,
                "belongs_to-0-food_name": self.ing1.food.name,
                "belongs_to-0-notes": "",
                "belongs_to-0-DELETE": "",
                "belongs_to-1-id": ing3.pk,
                "belongs_to-1-recipe": self.rec1.pk,
                "belongs_to-1-amount": ing3.amount,
                "belongs_to-1-unit": ing3.unit,
                "belongs_to-1-food_name": ing3.food.name,
                "belongs_to-1-notes": "",
                "belongs_to-1-DELETE": "on",
                "directions": self.rec1.directions,
                "categories": self.cat1.pk,
                "image": "",
            },
        )
        self.assertEqual(self.rec1.get_ingredients().count(), 1)
        self.assertEqual(Ingredient.objects.filter(recipe=self.rec1.pk).count(), 1)

    def test_ingredient_alteration_on_update(self):
        self.create_dummy_data()
        ing3 = Ingredient.objects.create(
            amount=3,
            unit="testUnit3",
            food=self.food3,
            notes="TestNote",
            recipe=self.rec1,
        )
        self.assertEqual(Ingredient.objects.filter(recipe=self.rec1.pk).count(), 2)
        self.client.login(username="testUser", password="testPassword")
        re = self.client.post(
            f"/recipe/{self.rec1.pk}/update/",
            {
                "title": self.rec1.title,
                "prep_time": self.rec1.prep_time,
                "servings": self.rec1.servings,
                "belongs_to-TOTAL_FORMS": "3",
                "belongs_to-INITIAL_FORMS": "2",
                "belongs_to-MIN_NUM_FORMS": "0",
                "belongs_to-MAX_NUM_FORMS": "1000",
                "belongs_to-0-id": self.ing1.pk,
                "belongs_to-0-recipe": self.rec1.pk,
                "belongs_to-0-amount": self.ing1.amount,
                "belongs_to-0-unit": self.ing1.unit,
                "belongs_to-0-food_name": self.ing1.food.name,
                "belongs_to-0-notes": "",
                "belongs_to-0-DELETE": "",
                "belongs_to-1-id": ing3.pk,
                "belongs_to-1-recipe": self.rec1.pk,
                "belongs_to-1-amount": 4,
                "belongs_to-1-unit": "TestUnit4",
                "belongs_to-1-food_name": "Food4",
                "belongs_to-1-notes": "",
                "belongs_to-1-DELETE": "",
                "directions": self.rec1.directions,
                "categories": self.cat1.pk,
                "image": "",
            },
        )
        self.assertEqual(self.rec1.get_ingredients().count(), 2)
        ing = Ingredient.objects.get(unit="TestUnit4")
        self.assertEqual(ing.amount, 4)
        self.assertEqual(ing.unit, "TestUnit4")

    def test_user_can_not_update_others_recipes(self):
        self.create_dummy_data()
        self.client.login(username="testUser2", password="testPassword2")
        url = f"/recipe/{self.rec1.pk}/update/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_user_can_not_delete_others_recipes(self):
        self.create_dummy_data()
        self.client.login(username="testUser2", password="testPassword2")
        url = f"/recipe/{self.rec1.pk}/delete/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_user_can_update_own_recipes(self):
        self.create_dummy_data()
        self.client.login(username="testUser", password="testPassword")
        url = f"/recipe/{self.rec1.pk}/update/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_can_delete_own_recipes(self):
        self.create_dummy_data()
        self.client.login(username="testUser", password="testPassword")
        url = f"/recipe/{self.rec1.pk}/delete/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
 """
