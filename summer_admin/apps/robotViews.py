import json

from django.http import JsonResponse
from django.core.cache import cache
from summer_admin.apps.models import Users, Charge, Agent_charge
from summer_admin.robot.robot import config
from summer_admin.rpc.rpc import *
from summer_admin.apps.views import *
import datetime
from django.shortcuts import render

from summer_admin.robot import robot


def create_room(request):
    account = str(request.GET['account'])
    password = str(request.GET['password'])
    room_type = request.GET['type']
    rtn = robot.create_room(account, password, room_type)
    print(rtn)
    return JsonResponse(json.loads(rtn))


def get_room_info(request):
    room_id = str(request.GET['roomId'])
    rtn = robot.get_room_info(room_id)
    d = json.loads(rtn)
    code = d['code']
    service = d['service']
    rule = ""
    if code == 0:

        roomType = d["params"]["roomType"]
        if roomType == 2:
            rule = get_poker_room_rule(d["params"])
        elif roomType == 1:
            rule = get_majiang_room_rule(d["params"])

    else:
        d["params"] = {"roomId" : "（该房间不存在或已解散）"}

    d['rule'] = rule
    d['category'] =  config.get('robot', 'gameCategory')
    return render(request, 'roomInfo.html', {"data" : d})
    # return JsonResponse(json.loads(rtn))


def get_poker_room_rule(data):

    rs = None
    try:
        roomType = data["gameType"]
        limited = data["multiple"]
        roomEach = data["isAA"]
        roomAgency = data["isCreaterJoin"]
        roomId = data["roomId"]
        gameNumber = data["gameNumber"]

        limitedStr = None
        gameType = None

        if roomId == "" or roomId == None:
            roomId = "（该房间不存在或已解散）"

        if limited == "-1":
            limitedStr = "炸不封顶"
        elif limited == "3":
            limitedStr = "3炸封顶"
        elif limited == "4":
            limitedStr = "4炸封顶"
        elif limited == "5":
            limitedStr = "5炸封顶"

        if roomType == "3" or roomType == "4":
            gameType = "临汾斗地主"
        else:
            gameType = "标准斗地主"

        optionStr = ""

        if roomEach == True:
            optionStr += " 3人建房"
        else:
            if roomAgency == True:
                optionStr += " 代建房"
            else:
                optionStr += " 房主建房"

        rs = "龙七棋牌" + str(gameType) + "、" + "房间ID：" + str(roomId) + "、" + str(
            gameNumber) + "局、" + limitedStr + optionStr
    except:
        rs = ""

    return rs

def get_majiang_room_rule(data):

    try:
        type = data["modeTotal"]
        roomType = data["each"]
        turn = data["gameNumber"]
        multiple = data["multiple"]
        option = data["mode"]
        roomId = data["roomId"]
        if roomId == "" or roomId == None:
            roomId = "（该房间不存在或已解散）"

        context = None
        huangStr = None

        if type == "1":
            context = "扣点"
        elif type == "2":
            if option == "3" and roomType == "3":
                context = "点炮胡"
            else:
                if option == "1" or option == "3":
                    context = "平胡"
                else:
                    context = "大胡"
        elif type == "15":
            context = "硬三嘴"
            huangStr = "\n荒庄时,下家坐庄"
        elif type == "4":
            context = "拐三角胡"
        elif type == "5":
            context = "立四"

        if option == "6":
            context += ",清一色,一条龙"
        elif option == "1" or option == "2":
            context += ""
        elif option == "3":
            if roomType == "3":
                pass
            else:
                context += ""
        elif option == "4":
            context += ""

        if ((int(option) >> 10) & 1) == 1:
            context += ",一门牌"
            context = context.replace("硬三嘴", "", 2)
            huangStr = "\n荒庄时,下家坐庄"

        if ((int(option) >> 11) & 1) == 1:
            context += ",数页"

        title = "房间号" + roomId

        if roomType == "0":
            title += "(房主建房)"
        elif roomType == "1":
            title += "(4人建房)"
        elif roomType == "2":
            title += "(代建房)"

        title += ",三缺一"
        context += str(turn) + "局" + str(multiple) + "倍" + huangStr
        return title  + context

    except:
        return ""









