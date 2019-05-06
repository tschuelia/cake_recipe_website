# Generated by Django 2.2 on 2019-05-04 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0015_auto_20190504_0734'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='recipe',
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(blank=True, to='recipes.Ingredient'),
        ),
    ]