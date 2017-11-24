from django.http import JsonResponse
from django.shortcuts import render
from summer_admin.robot.robot import config
from summer_admin.apps.views import *

def officail_web(request):
    category = config.get('robot', 'gameCategory')
    url = None;
    game_name = None
    if category == "tongcheng":
        url = "http://fir.im/ncdp"
        game_name = "河北同城麻将"
    elif category == "laotie":
        url = "http://fir.im/ncjb"
        game_name = "老铁棋牌"
    else:
        url = ""
        game_name = ""
    dict = {"url": url, "category": category, "game_name" : game_name}
    return render(request, "officialWeb.html", {"data": dict})