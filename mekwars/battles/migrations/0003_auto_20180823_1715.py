# Generated by Django 2.1 on 2018-08-24 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battles', '0002_auto_20180823_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='type',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='unit',
            name='value',
            field=models.IntegerField(default=0),
        ),
    ]
