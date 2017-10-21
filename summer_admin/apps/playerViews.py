import json

from django.http import JsonResponse
from django.core.cache import cache
from summer_admin.apps.models import Users, Charge, Agent_charge
from summer_admin.rpc.rpc import *
from summer_admin.apps.views import *
import datetime
@check_login
def charge(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']

    param = json.loads(str(request.GET['chargeForm']))
    user_id = int(str(param['userId']))
    num = int(str(param['num']))

    array = Agent_user.objects.filter(id=agent_id)
    entry_list = list(array.all())
    leng = len(entry_list)

    if leng == 0:
        return JsonResponse({'code': 100, 'data': '充值失败'})

    agent_user = entry_list[0]

    if agent_user.money < num:
        return JsonResponse({'code': 100, 'data': '充值失败'})

    rpc_client = get_client()

    order = Order(userId=user_id, num=num, type=ChargeType.money, agentId=agent_id)
    rtn = rpc_client.charge(order)
    if rtn == 0:
        agent_user.money -= num
        agent_user.save()
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

        print(data)

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
    total_page = len(player_data)
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
        total_page = len(player_data)
        data = {'tableData': player_data, 'totalPage': total_page}
        return JsonResponse({'code': 20000, 'data': data})

    array = Agent_charge.objects.filter(agent_id=title)
    player_data = list(array.values()[index_left:index_right])
    total_page = len(player_data)
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
    total_page =  len(player_data)
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

    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']

    agent_name = dict['username']
    array = None

    if agent_name == 'admin':
        array = Agent_user.objects.filter(username__contains=title)
    else:
        array = Agent_user.objects.filter(username__contains=title, parent_id=agent_id)
    player_data = list(array.values()[index_left:index_right])
    total_page = len(player_data)
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})

@check_login
#超级管理员删除代理
def delete_delegate(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    username = dict['username']

    if username == 'admin':
        pass
    else:
        pass

@check_login
def agent_fetch_slf(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    array = Agent_user.objects.filter(id = agent_id)
    player_data = list(array.values()[0:1])
    total_page = len(player_data)
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})


