from django.db import models


class Battle(models.Model):
    datetime = models.CharField(max_length=50, default='')
    winner = models.CharField(max_length=50, default='')
    loser = models.CharField(max_length=50, default='')
    faction_won = models.CharField(max_length=100, default='')
    faction_lost = models.CharField(max_length=100, default='')
    location = models.CharField(max_length=100, default='')


class Unit(models.Model):
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE)
    unit_id = models.IntegerField(default=0)  # mekwars unit id
    owner = models.CharField(max_length=50, default='')
    chassis = models.CharField(max_length=50, default='')
    model = models.CharField(max_length=50, default='')
    type = models.IntegerField(default=0)
    battle_value = models.IntegerField(default=0)
    value = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='')
    destroyed_by = models.CharField(max_length=50, default='', null=True)


