# Generated by Django 2.2 on 2019-04-27 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default='recipe_pics/default.jpg', upload_to='recipe_pics'),
        ),
    ]
