from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.template import loader
from django.db.models import Q
from .models import Battle, Unit
import json
import os

with open("battles\\app_settings.json") as json_appData:
    app_settings = json.load(json_appData)
    path = app_settings['path']
    path_processed = app_settings['path_processed']
    path_player = app_settings['path_player']
    server_name = app_settings['server_name']
    path_img_mek = app_settings['path_img_mek']
    path_img_vee = app_settings['path_img_vee']
    path_img_aero = app_settings['path_img_aero']
    path_img_inf = app_settings['path_img_inf']
    path_img_ba = app_settings['path_img_ba']


def index(request):
    # process battles if any exist in directory
    for filename in os.listdir(path):
        if filename.endswith(".json"):
            with open(path+filename) as json_data:
                battle_info = json.load(json_data)
                this_battle = Battle()
                this_battle.datetime = battle_info['datetime']
                this_battle.winner = battle_info['winner']
                this_battle.loser = battle_info['loser']
                this_battle.faction_won = battle_info['faction_won']
                this_battle.faction_lost = battle_info['faction_lost']
                this_battle.location = battle_info['location']
                this_battle.save()
                # process units in the battle
                for curr_unit in battle_info['units']:
                    new_unit = Unit()
                    new_unit.battle_id = this_battle.pk
                    new_unit.unit_id = curr_unit['unit_id']
                    new_unit.owner = curr_unit['owner']
                    new_unit.chassis = curr_unit['chassis']
                    new_unit.model = curr_unit['model']
                    new_unit.type = curr_unit['type']
                    new_unit.battle_value = curr_unit['battle_value']
                    new_unit.value = curr_unit['value']
                    new_unit.status = curr_unit['status']
                    new_unit.destroyed_by = curr_unit['destroyed_by']
                    new_unit.save()
        # move json file to processed folder
        if not os.path.exists(path_processed):
            os.makedirs(path_processed)
        os.rename(path+filename, path_processed+filename)
        if os.path.exists(path+filename):
            os.remove(path+filename)
    # start processing request , get last 15 battles
    all_battles = Battle.objects.order_by('-id')[:15]
    template = loader.get_template('battles/index.html')
    context = {
        'all_battles': all_battles,
        'server_name': server_name
    }
    return HttpResponse(template.render(context, request))


def detail(request, battle_id):
    # Get all units that have the requested battle_id
    units = Unit.objects.all().filter(battle=battle_id)
    battle = Battle.objects.all().filter(pk=battle_id)
    battle = battle.get(pk=battle_id)
    # From the units in this battle, sort out ownership between the players
    winner_units = Unit.objects.all().filter(battle=battle_id, owner=battle.winner)
    loser_units = Unit.objects.all().filter(battle=battle_id, owner=battle.loser)
    # Calculate losses in cbills and bv
    winner_losses = 0
    winner_bvlost = 0
    loser_losses = 0
    loser_bvlost = 0
    for unit in winner_units:
        if unit.status == "dead":
            winner_losses += unit.value
            winner_bvlost += unit.battle_value
    for unit in loser_units:
        if unit.status == "dead":
            loser_losses += unit.value
            loser_bvlost += unit.battle_value
    # Get mekwars player info in json format (part of discord bot options)
    with open(path_player+battle.winner+'.json') as json_data:
        winner_info = json.load(json_data)
    with open(path_player+battle.loser+'.json') as json_data:
        loser_info = json.load(json_data)
    # Set template and context
    template = loader.get_template('battles/detail.html')
    context = {
        'units': units,
        'battle': battle,
        'winner_units': winner_units,
        'loser_units': loser_units,
        'winner_losses': winner_losses,
        'winner_bvlost': winner_bvlost,
        'loser_losses': loser_losses,
        'loser_bvlost': loser_bvlost,
        'winner_info': winner_info,
        'loser_info': loser_info,
        'server_name': server_name,
        'path_img_mek': path_img_mek,
        'path_img_vee': path_img_vee,
        'path_img_aero': path_img_aero,
        'path_img_inf': path_img_inf,
        'path_img_ba': path_img_ba
    }
    return HttpResponse(template.render(context, request))


def bio(request, username):
    # get json data for username
    with open(path_player+username+'.json') as json_data:
        user_info = json.load(json_data)
    # get battles won and lost
    all_battles = Battle.objects.order_by('-id').filter(Q(winner=username) | Q(loser=username))
    battles_won = Battle.objects.order_by('-id').filter(winner=username)
    battles_lost = Battle.objects.order_by('-id').filter(loser=username)
    ratio = safe_div(battles_won.count(), battles_won.count()+battles_lost.count()) * 100
    # get units destroyed and units lost
    units_destroyed = Unit.objects.filter(destroyed_by=username)
    units_lost = Unit.objects.filter(owner=username, status='dead')
    unit_ratio = safe_div(units_destroyed.count(), units_destroyed.count() + units_lost.count()) * 100
    # count battle value stats
    bv_destroyed = 0
    bv_lost = 0
    for unit in units_destroyed:
        bv_destroyed += unit.battle_value
    for unit in units_lost:
        bv_lost += unit.battle_value
    bv_ratio = safe_div(bv_destroyed, bv_destroyed+bv_lost) * 100
    # count value stats
    val_destroyed = 0
    val_lost = 0
    for unit in units_destroyed:
        val_destroyed += unit.value
    for unit in units_lost:
        val_lost += unit.value
    val_ratio = safe_div(val_destroyed, val_destroyed+val_lost) * 100
    template = loader.get_template('battles/bio.html')
    context = {
        'all_battles': all_battles,
        'battles_won': battles_won,
        'user_info': user_info,
        'battles_lost': battles_lost,
        'wins': battles_won.count(),
        'losses': battles_lost.count(),
        'ratio': ratio,
        'units_destroyed': units_destroyed.count(),
        'units_lost': units_lost.count(),
        'unit_ratio': unit_ratio,
        'bv_lost': bv_lost,
        'bv_destroyed': bv_destroyed,
        'bv_ratio': bv_ratio,
        'val_lost': val_lost,
        'val_destroyed': val_destroyed,
        'val_ratio': val_ratio,
        'server_name': server_name
    }
    return HttpResponse(template.render(context, request))


def search(request):
    search_id = request.GET.get('playersearch')
    user_set = Battle.objects.filter(Q(winner=search_id) | Q(loser=search_id))
    forward_to = '/battles/bio/'+search_id+'/'
    html = '<h1>user_set is null?</h1>' + search_id
    if request.GET.get('playersearch'):
        if user_set.count() > 0:
            return HttpResponseRedirect(forward_to)
        elif user_set.count() == 0:
            return HttpResponseNotFound('<h1>Player not found<br><a href="/battles/"> GO BACK TO MAIN PAGE</a></h1>')
    else:
        return HttpResponse('<h1>You did not enter a name<br><a href="/battles/"> GO BACK TO MAIN PAGE</a></h1>')


def safe_div(x, y):
    if y == 0:
        return 0
    return x / y
