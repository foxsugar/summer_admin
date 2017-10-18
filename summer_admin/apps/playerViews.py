import json

from django.http import JsonResponse

from summer_admin.apps.models import Users, Charge, Agent_charge
from summer_admin.rpc.rpc import *


def charge(request):
    param = json.loads(str(request.GET['chargeForm']))
    user_id = int(str(param['userId']))
    num = int(str(param['num']))
    rpc_client = get_client()
    agent_id = 1
    print(rpc_client.getUserInfo(1))
    order = Order(userId=user_id, num=num, type=ChargeType.money, agentId=0)
    rtn = rpc_client.charge(order)
    if rtn == 0:
        return JsonResponse({'code': 20000, 'data': '充值成功'})
    else:
        return JsonResponse({'code': 100, 'data': '充值失败'})


def user_list(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['size']))
    index_left = (page - 1) * size
    index_right = page * size
    # user_data = list(Users.objects.values()[page:page_right])
    user_data = list(Users.objects.values()[index_left:index_right])

    total_page = Users.objects.count()

    data = {'tableData': user_data, 'totalPage': total_page}

    return JsonResponse({'code': 20000, 'data': data})

def charge_list(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['size']))
    index_left = (page - 1) * size
    index_right = page * size
    total_page = Charge.objects.count()
    player_data = list(Charge.objects.values()[index_left:index_right])
    data = {'tableData': player_data, 'totalPage': total_page}

    return JsonResponse({'code': 20000, 'data': data})

def agent_charge_list(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['size']))
    index_left = (page - 1) * size
    index_right = page * size
    total_page = Agent_charge.objects.count()
    agent_data = list(Agent_charge.objects.values()[index_left:index_right])
    data = {'tableData': agent_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})
