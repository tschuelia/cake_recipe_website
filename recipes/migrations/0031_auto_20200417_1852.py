# Generated by Django 3.0.5 on 2020-04-17 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0030_auto_20200417_1849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='related_recipes',
            field=models.ManyToManyField(blank=True, related_name='_recipe_related_recipes_+', to='recipes.Recipe', verbose_name='zugehörige Rezepte'),
        ),
    ]