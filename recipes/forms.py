from django import forms
from django.urls import reverse_lazy
from django_addanother.widgets import AddAnotherWidgetWrapper
from .models import Recipe, Ingredient, Food, Image

from django.forms import inlineformset_factory, modelformset_factory


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        exclude = ["author"]
        widgets = {
            "categories": AddAnotherWidgetWrapper(
                forms.SelectMultiple, reverse_lazy("category-create"),
            )
        }


class IngredientForm(forms.ModelForm):
    food_name = forms.CharField(label="Lebensmittel", required=True)

    class Meta:
        model = Ingredient
        fields = ["amount", "unit", "food_name", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["food_name"].initial = self.instance.food.name

    def save(self, commit):
        ingredient = super().save(commit=False)
        food_obj, created = Food.objects.get_or_create(
            name=self.cleaned_data["food_name"]
        )
        ingredient.food = food_obj
        if commit:
            ingredient.save()
        return ingredient


IngredientFormSet = inlineformset_factory(
    Recipe,
    Ingredient,
    form=IngredientForm,
    extra=1,
    widgets={
        "notes": forms.Textarea(attrs={"cols": 20, "rows": 1}),
        "amount": forms.NumberInput(attrs={"style": "width:80px"}),
        "unit": forms.TextInput(attrs={"style": "width:80px"}),
    },
)


class ImageForm(forms.ModelForm):
    image = forms.ImageField(label="")

    class Meta:
        model = Image
        fields = [
            "image",
        ]

    def save(self, commit):
        image = super().save(commit=False)
        img_obj, created = Image.objects.get_or_create(
            image=image.image, recipe=image.recipe
        )
        if commit:
            img_obj.save()
        return img_obj


ImageFormSet = inlineformset_factory(
    Recipe, Image, form=ImageForm, fields=("image",), extra=1
)
