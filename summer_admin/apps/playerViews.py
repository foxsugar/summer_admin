import json

from django.http import JsonResponse
from django.core.cache import cache
from summer_admin.apps.models import Users, Charge, Agent_charge
from summer_admin.rpc.rpc import *
from summer_admin.apps.views import *

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

@check_login
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


@check_login
def charge_list(request):

    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    username = dict['username']

    if username != 'admin':

        page = int(str(request.GET['page']))
        size = int(str(request.GET['size']))
        index_left = (page - 1) * size
        index_right = page * size

        array = Charge.objects.filter(origin=agent_id)
        player_data = list(array.values()[index_left:index_right])
        total_page = len(player_data)
        data = {'tableData': player_data, 'totalPage': total_page}
        return JsonResponse({'code': 20000, 'data': data})

    else:
        page = int(str(request.GET['page']))
        size = int(str(request.GET['size']))
        index_left = (page - 1) * size
        index_right = page * size
        total_page = Charge.objects.count()
        player_data = list(Charge.objects.values()[index_left:index_right])
        data = {'tableData': player_data, 'totalPage': total_page}
        return JsonResponse({'code': 20000, 'data': data})

@check_login
def agent_charge_list(request):

    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']

    username = dict['username']
    if username != 'admin':

        page = int(str(request.GET['page']))
        size = int(str(request.GET['size']))
        index_left = (page - 1) * size
        index_right = page * size

        array = Agent_charge.objects.filter(agent_id=agent_id)
        agent_data = list(array.values()[index_left:index_right])
        total_page = len(array)
        data = {'tableData': agent_data, 'totalPage': total_page}
        return JsonResponse({'code': 20000, 'data': data})

    else:
        page = int(str(request.GET['page']))
        size = int(str(request.GET['size']))
        index_left = (page - 1) * size
        index_right = page * size
        total_page = Agent_charge.objects.count()
        agent_data = list(Agent_charge.objects.values()[index_left:index_right])
        data = {'tableData': agent_data, 'totalPage': total_page}
        return JsonResponse({'code': 20000, 'data': data})

def logout(request):

    cache.clear()
    return JsonResponse({'code': 20000, 'data': None})

@check_login
def search_player(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['limit']))
    index_left = (page - 1) * size
    index_right = page * size
    title = None
    try:
        title = str(request.GET['title'])
    except:
        title = ""

    array = Charge.objects.filter(username__contains=title)
    player_data = list(array.values()[index_left:index_right])
    total_page = len(player_data) / size + 1
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})

@check_login
def search_agent_charge(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['limit']))
    index_left = (page - 1) * size
    index_right = page * size
    title = None

    try:
        title = str(request.GET['title'])
    except:
        player_data = []
        total_page = 1
        data = {'tableData': player_data, 'totalPage': total_page}
        return JsonResponse({'code': 20000, 'data': data})

    array = Agent_charge.objects.filter(agent_id=title)
    player_data = list(array.values()[index_left:index_right])
    total_page = len(player_data) / size + 1
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})

@check_login
def serarch_player_list(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['limit']))
    index_left = (page - 1) * size
    index_right = page * size
    title = None

    try:
        title = str(request.GET['title'])
    except:
        title = ""

    array = Users.objects.filter(username__contains=title)
    player_data = list(array.values()[index_left:index_right])
    total_page = len(player_data) / size + 1
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})

@check_login
def fetch_delegates(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['limit']))
    index_left = (page - 1) * size
    index_right = page * size
    title = None

    try:
        title = str(request.GET['title'])
    except:
        title = ""

    array = Agent_user.objects.filter(username__contains=title)
    player_data = list(array.values()[index_left:index_right])
    total_page = len(player_data) / size + 1
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})
    pass
