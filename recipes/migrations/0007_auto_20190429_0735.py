# Generated by Django 2.2 on 2019-04-29 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_recipe_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='categories',
            field=models.ManyToManyField(blank=True, to='recipes.Category'),
        ),
    ]