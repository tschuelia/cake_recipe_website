# Generated by Django 3.1.6 on 2021-02-07 14:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0037_recipe_secret_notes'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Image',
            new_name='RecipeImage',
        ),
    ]