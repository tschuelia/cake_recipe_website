# Generated by Django 3.0.5 on 2020-04-19 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0033_auto_20200417_2013'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='public',
            field=models.BooleanField(default=False, verbose_name='öffentlich'),
        ),
    ]
