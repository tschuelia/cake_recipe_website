from django.test import TestCase
import unittest
from django.test import Client

from django.contrib.auth.models import User

from .forms import IngredientFormSet, IngredientForm
from .models import Food, Ingredient, Category, Recipe

class Test(TestCase):
    def setUp(self):
        self.client = Client()


    def test_food_and_ingredient_created(self):
        '''
        Test whether IngredientForm.save() works properly and saves Ingrdient and Food in case both did not exist yet
        '''
        self.assertEqual(len(Ingredient.objects.all()), 0)
        self.assertEqual(len(Food.objects.all()), 0)

        ingredient_data = {'amount': 500, 'unit': 'g', 'food_name': 'Mehl', 'notes':'Note'}
        form = IngredientForm(data=ingredient_data)
        form.save(True)
        self.assertEqual(len(Ingredient.objects.all()), 1)
        self.assertEqual(len(Food.objects.all()), 1)
        food = Food.objects.first()
        self.assertEqual(food.name, 'Mehl')
        ing = Ingredient.objects.first()
        self.assertEqual(ing.amount, 500)
        self.assertEqual(ing.unit, 'g')
        self.assertEqual(ing.notes, 'Note')
        self.assertEqual(ing.food, food)

    def test_create_recipe_view(self):
        cat1 = Category.objects.create(title = 'Cat1')
        user = User.objects.create_user('testUser', 'test@test.com', 'testPassword')
        self.client.login(username='testUser', password='testPassword')
        re = self.client.post('/recipe/new/', {
            'title': 'Rec1',
            'belongs_to-TOTAL_FORMS': '1',
            'belongs_to-INITIAL_FORMS': '0',
            'belongs_to-MIN_NUM_FORMS': '0',
            'belongs_to-MAX_NUM_FORMS': '1000',
            'belongs_to-0-id': '',
            'belongs_to-0-recipe': '',
            'belongs_to-0-amount': '100',
            'belongs_to-0-unit': 'TestUnit',
            'belongs_to-0-food_name': 'TestFood',
            'belongs_to-0-notes': 'TestNote',
            'belongs_to-0-DELETE': '',
            'directions': 'bake',
            'prep_time': '1h',
            'categories': cat1.pk
        })
        recipe = Recipe.objects.get(title='Rec1')
        self.assertEqual(recipe.directions, 'bake')
        self.assertEqual(recipe.prep_time, '1h')
        self.assertEqual([cat.pk for cat in recipe.get_categories()], [cat1.pk])
        self.assertEqual(recipe.author, user)
        self.assertEqual(recipe.image, 'default.jpg')

        self.assertEqual(len(Food.objects.all()), 1)
        food = Food.objects.first()
        self.assertEqual(food.name, 'TestFood')

        self.assertEqual(len(Ingredient.objects.all()), 1)
        ing = Ingredient.objects.first()
        self.assertEqual(ing.amount, 100)
        self.assertEqual(ing.unit, 'TestUnit')
        self.assertEqual(ing.notes, 'TestNote')
        self.assertEqual(ing.food, food)

        url = f'/recipe/{recipe.pk}/'
        self.assertRedirects(re, url)

    def create_dummy_data(self):
        self.user1 = User.objects.create_user('testUser', 'test@test.com', 'testPassword')
        self.user2 = User.objects.create_user('testUser2', 'test2@test.com', 'testPassword2')

        self.cat1 = Category.objects.create(title = 'Cat1')
        self.cat2 = Category.objects.create(title = 'Cat2')

        self.food1 = Food.objects.create(name = 'Food1')
        self.food2 = Food.objects.create(name = 'Food2')

        self.rec1 = Recipe.objects.create(title = 'Rec1', directions = 'Dir1', prep_time = '1', author=self.user1)
        self.rec2 = Recipe.objects.create(title = 'Rec2', directions = 'Dir2', prep_time = '2', author=self.user2)
        self.rec1.categories.add(self.cat1)
        self.rec2.categories.add(self.cat2)

        self.ing1 = Ingredient.objects.create(amount = 1, unit = 'testUnit1', food = self.food1, notes='', recipe=self.rec1)
        self.ing2 = Ingredient.objects.create(amount = 2, unit = 'testUnit2', food = self.food2, notes='TestNote', recipe=self.rec2)

    def test_user_can_not_update_others_recipes(self):
        self.create_dummy_data()
        self.client.login(username='testUser2', password='testPassword2')
        url = f'/recipe/{self.rec1.pk}/update/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_user_can_not_delete_others_recipes(self):
        self.create_dummy_data()
        self.client.login(username='testUser2', password='testPassword2')
        url = f'/recipe/{self.rec1.pk}/delete/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_user_can_update_own_recipes(self):
        self.create_dummy_data()
        self.client.login(username='testUser', password='testPassword')
        url = f'/recipe/{self.rec1.pk}/update/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_can_delete_own_recipes(self):
        self.create_dummy_data()
        self.client.login(username='testUser', password='testPassword')
        url = f'/recipe/{self.rec1.pk}/update/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
