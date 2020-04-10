from django.apps import AppConfig
from watson import search as watson


class RecipesConfig(AppConfig):
    name = "recipes"

    def ready(self):
        Recipe = self.get_model("Recipe")
        watson.register(Recipe)
