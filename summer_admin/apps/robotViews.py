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


def send_message(request):
    account = str(request.GET['account'])
    password = str(request.GET['password'])
    message = request.GET['message']
    rtn = robot.send_message(account, password, message)
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
        if roomType == '2':
            rule = get_poker_room_rule(d["params"])
        elif roomType == '1':
            rule = get_majiang_room_rule(d["params"])
        d["params"]["roomId"] = room_id
    else:
        d["params"] = {"roomId": "（该房间不存在或已解散）"}

    d['rule'] = rule
    d['category'] = config.get('robot', 'gameCategory')
    return render(request, 'roomInfo.html', {"data": d})
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

        if limited == -1:
            limitedStr = "炸不封顶"
        elif limited == 3:
            limitedStr = "3炸封顶"
        elif limited == 4:
            limitedStr = "4炸封顶"
        elif limited == 5:
            limitedStr = "5炸封顶"

        if roomType == '3' or roomType == '4':
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

        rs = '龙七棋牌、%s、房间ID：%s、%s局、%s%s%s' % (
        str(gameType), str(roomId), str(gameNumber), str(gameType), limitedStr, optionStr)
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
        yiPaoDuoXiang = data["yipaoduoxiang"]
        peopleNum = data["personNumber"]
        clubId = ""

        try:
            data["clubRoomModel"]
        except:
            pass

        gps = False
        try:
            if ((int(data["otherMode"]) >> 1) & 1) == 1:
                gps = True
        except:
            pass

        if roomId == "" or roomId == None:
            roomId = "（该房间不存在或已解散）"

        gameTypeName = ""
        context = ""
        huangStr = ""

        isZiMo = False
        isCanChi = False
        isCanTing = False

        try:
            isZiMo = data["mustZimo"]
            isCanChi = data["canChi"]
            isCanTing = data["haveTing"]

        except:
            pass

        if type == "1":
            context = "扣点"
            if option == "6":
                context = context + ",清一色,一条龙,加倍"
        # 推到胡
        elif type == "2":
            if option == "1" or option == "3" or option == "11" or option == "13":
                gameTypeName = "平胡"
            else:
                gameTypeName = "大胡"

            if option == "1" or option == "2":
                context += ",带风,不报听"
            if option == "3":
                context += ",不带风,不报听"
            if option == "4":
                context += ",不带风,不报听"
            if option == "11" or option == "12":
                if type != "30":
                    context += ",带风,报听"
            if option == "13" or option == "14":
                context += ",不带风,报听"
            # context += yiPaoDuoXiang ? ",一炮多响": ""
            if yiPaoDuoXiang:
                context += ",一炮多响"
            if isZiMo:
                context += ",只可自摸"
        elif type == "15":
            # context = "硬三嘴"
            gameTypeName = "硬三嘴";
            huangStr = "荒庄时,下家坐庄"

            if (int(option) >> 10) & 1 == 1:
                gameTypeName = "一门牌"
            if (int(option) >> 11) & 1 == 1:
                context += ",数页"
        elif type == "4":
            context = "拐三角胡"
        elif type == "5":
            context = "立四"
        elif type == "31":
            context = "撵中子"
            if option == "2":
                context += ",1中子"
            else:
                context += ",2中子"

            if isCanChi:
                context += ",带吃"
            else:
                context += ",不带吃"

            if isCanTing:
                context += ",报听"
            else:
                context += ",不报听"

            if isZiMo:
                context += ",只可自摸"

        if type == "34":
            gameTypeName = "扭叶子"
            if option == "1":
                context += ",庄+1分"
            elif option == "2":
                context += ",庄+2分"
            elif option == "4":
                context += ",庄+3分"
            else:
                context += ",庄+4分"

            if isZiMo:
                context += ",只可自摸"

        if type == "100":
            gameTypeName = "侯马推倒胡"
            if isZiMo:
                context += ",只可自摸"

        if gps:
            context += ",防作弊模式"

        personType = ""

        if peopleNum == "2":
            personType = "2人麻将"
        if peopleNum == "3":
            personType = "3人麻将"
        if peopleNum == "4":
            personType = "4人麻将"

        club = ""

        if clubId != None:
            title = "亲友圈房间号：" + roomId
            club = ",亲友圈号：" + clubId
        else:
            title = "房间号：" + roomId

            if roomType == "0":
                title += "(房主建房)"
            if roomType == "1":
                title += "(AA建房)"
            if roomType == "2":
                title += "(代建房)"

        ss = ""
        if type != 100:
            ss = "局"
        else:
            ss = "圈"

        finalStr = "%s,%s,%s,%s,%s倍%s%s" % (gameTypeName,personType,turn, ss,multiple,context,huangStr)
        return  finalStr
    except:
        return ""
