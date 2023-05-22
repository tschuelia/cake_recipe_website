# Generated by Django 3.2.12 on 2023-05-21 18:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0041_auto_20221107_1724'),
    ]

    operations = [
        migrations.CreateModel(
            name='Idea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Titel')),
                ('notes', models.TextField(blank=True, verbose_name='Notiz')),
                ('url', models.URLField(blank=True, verbose_name='Link')),
                ('user', models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL))
            ],
        ),
        migrations.AlterField(
            model_name='shoppinglistrecipe',
            name='servings',
            field=models.DecimalField(decimal_places=3, max_digits=6, verbose_name='Anzahl'),
        ),
    ]