import json

from django.http import JsonResponse

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
