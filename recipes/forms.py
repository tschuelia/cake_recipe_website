from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory, modelformset_factory
from django.urls import reverse_lazy
from django_addanother.widgets import AddAnotherWidgetWrapper

from .models import Category, Food, Image, Ingredient, Recipe


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        exclude = ["author"]
        widgets = {
            "categories": AddAnotherWidgetWrapper(
                forms.SelectMultiple(
                    attrs={
                        "class": "selectpicker",
                        "data-live-search": "true",
                        "data-size": "5",
                        "title": "Wähle Kategorien",
                    }
                ),
                reverse_lazy("category-create"),
            ),
            "related_recipes": forms.SelectMultiple(
                attrs={
                    "class": "selectpicker",
                    "data-live-search": "true",
                    "data-size": "5",
                    "title": "Suche nach Rezepten",
                }
            ),
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
        fields = ["image", "is_primary"]

    def save(self, commit):
        image = super().save(commit=False)
        img_obj, created = Image.objects.get_or_create(
            image=image.image, recipe=image.recipe
        )
        img_obj.is_primary = image.is_primary
        if commit:
            img_obj.save()
        return img_obj


class BaseImageFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        selected_any_as_primary = False
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue

            if selected_any_as_primary and form.cleaned_data.get("is_primary"):
                raise forms.ValidationError(
                    message="Es kann nur ein Bild als Titelbild gewählt werden.",
                    code="invalid",
                )

            elif form.cleaned_data.get("is_primary"):
                selected_any_as_primary = True


ImageFormSet = inlineformset_factory(
    Recipe,
    Image,
    form=ImageForm,
    formset=BaseImageFormset,
    fields=("image", "is_primary",),
    extra=1,
)


class CategoryFilterForm(forms.Form):
    c = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                "class": "selectpicker",
                "data-live-search": "true",
                "data-size": "5",
                "title": "Suche in allen Kategorien",
            }
        ),
        required=False,
        label="Filtern nach Kategorien",
    )


class FoodFilterForm(forms.Form):
    f = forms.ModelMultipleChoiceField(
        queryset=Food.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                "class": "selectpicker",
                "data-live-search": "true",
                "data-size": "5",
            }
        ),
        required=False,
        label="Filtern nach Zutaten",
    )

    _and = forms.BooleanField(
        required=False, label="nur Rezepte die alle gewählten Zutaten enthalten",
    )
