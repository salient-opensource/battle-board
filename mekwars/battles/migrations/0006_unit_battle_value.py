# Generated by Django 2.1 on 2018-09-05 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battles', '0005_auto_20180828_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='battle_value',
            field=models.IntegerField(default=0),
        ),
    ]