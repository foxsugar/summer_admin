import json

from django.http import JsonResponse
from django.core.cache import cache
from summer_admin.apps.models import Users, Charge, Agent_charge
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
    return render(request, 'test.html', json.loads(rtn))
    # return JsonResponse(json.loads(rtn))
