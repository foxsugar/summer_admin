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
    elif category == "dxj":
        url = ""
        game_name = "xxx"
    else:
        url = ""
        game_name = ""
    dict = {"url": url, "category": category, "game_name" : game_name}
    return render(request, "officialWeb.html", {"data": dict})




def changeAgent(request):
    return render(request, "changeAgent.html", {})


def doChangeAgent(request):
    userId = request.GET['userId']
    newAgentId = request.GET['newAgentId']

    s = '玩家 '+userId + '  -> 绑定代理 ' + newAgentId

    rpc_client = get_client()

    re = '   '
    try:
        rtn = rpc_client.bindReferee(int(userId), int(newAgentId))
        if rtn == 0:
            re += "绑定成功"
        else:
            re += "绑定失败"
    except:
        re += '绑定失败'

    s += re
    return render(request, "changeAgent.html", {"data":s})