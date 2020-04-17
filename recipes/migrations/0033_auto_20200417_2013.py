# Generated by Django 3.0.5 on 2020-04-17 20:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0032_auto_20200417_1927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='recipe',
            field=models.ForeignKey(default=43, on_delete=django.db.models.deletion.CASCADE, related_name='belongs_to', to='recipes.Recipe'),
            preserve_default=False,
        ),
    ]
