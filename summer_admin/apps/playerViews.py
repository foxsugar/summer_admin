import json

from django.http import JsonResponse
from django.core.cache import cache
from summer_admin.apps.models import Users, Charge, Agent_charge
from summer_admin.rpc.rpc import *
from summer_admin.apps.views import *
import datetime
from django.db.models import Q

@check_login
def change_user_delegate(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
     # 总代理id
    agent_id = dict['id']
    # 需要修改的用户id
    dic = json.loads(str(request.GET['chargeForm']))
    pid = dic['id']
    # 需要修改的代理id
    aid  = int(dic['agent_id'])
    if agent_id != 1:
        return JsonResponse({'code': 101, 'data': '没有权限'})

    # Task.object.get(user_id=1)
    array = Agent_user.objects.filter(id=aid)
    entry_list = list(array.all())
    leng = len(entry_list)
    if leng == 0:
        return JsonResponse({'code': 100, 'data': '不存在该代理'})

    user = Users.objects.get(id=pid)
    user.referee = pid
    user.save()
    return JsonResponse({'code': 20000, 'data': aid})


@check_login
def charge_gold(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']

    param = json.loads(str(request.GET['chargeForm']))
    user_id = int(str(param['userId']))
    num = int(str(param['gold_num']))

    array = Agent_user.objects.filter(id=agent_id)
    entry_list = list(array.all())
    leng = len(entry_list)

    if leng == 0:
        return JsonResponse({'code': 100, 'data': '充值失败'})

    agent_user = entry_list[0]

    if agent_user.gold < num:
        return JsonResponse({'code': 100, 'data': '充值失败'})

    rpc_client = get_client()

    order = Order(userId=user_id, num=num, type=ChargeType.gold, agentId=agent_id)
    rtn = rpc_client.charge(order)
    rtn = 0
    if rtn == 0:
        agent_user.gold -= num
        agent_user.save()
        return JsonResponse({'code': 20000, 'data': '充值成功'})
    else:
        return JsonResponse({'code': 100, 'data': '充值失败'})

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

#奔驰宝马的代理接口
@check_login
def user_list_vip(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['size']))
    index_left = (page - 1) * size
    index_right = page * size
    # user_data = list(Users.objects.values()[page:page_right])
    # user_data = list(Users.objects.values()[index_left:index_right])

    #   array = Agent_user.objects.filter(username__contains=title, parent_id=agent_id)
    # player_data = list(array.values()[index_left:index_right])

    qset = Users.objects.filter(vip__gt=0)
    user_data = list(qset.values()[index_left:index_right])

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
def agent_change_state(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    username = dict['username']

    order_id = int(str(request.GET['id']))


    agent_charge = Agent_charge.objects.get(id = order_id)

    if agent_charge.charge_type == 9:
        agent_charge.charge_type = 10
    elif agent_charge.charge_type == 10:
        agent_charge.charge_type = 9

    agent_charge.save()

    data = None

    if agent_charge.charge_type == 9:
        data = "未打款"
    elif agent_charge.charge_type == 10:
        data = "已打款"

    return JsonResponse({'code': 20000, 'data': data})

#兑换记录
@check_login
def gold_cash_list(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']

    username = dict['username']

    page = int(str(request.GET['page']))
    size = int(str(request.GET['size']))
    index_left = (page - 1) * size
    index_right = page * size

    array = Agent_charge.objects.filter(Q(charge_type__startswith='9') | Q(charge_type__startswith='10'))
    agent_data = list(array.values()[index_left:index_right])
    total_page = len(array)

    for dict in agent_data:
        dict["gold_t"] = -dict["charge_num"]
        if dict["charge_type"] == 9:
            dict["ret"] = "未打款"
        else:
            dict["ret"] = "已打款"

    data = {'tableData': agent_data, 'totalPage': total_page}

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

# @check_login
def fetchplayer(request):
    player_id = int(str(request.GET['id']))
    array = Users.objects.filter(id=player_id)
    player_data = list(array.values()[0:1])
    total_page = len(player_data)
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})


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

#vip搜索
@check_login
def serarch_player_list_vip(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['limit']))
    index_left = (page - 1) * size
    index_right = page * size
    title = None

    try:
        title = str(request.GET['title'])
    except:
        title = ""
    #user.object.filter(Q(question__startswith='Who') | Q(question__startswith='What'))
    array = Users.objects.filter(username__contains=title, vip__gt=0)
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

#兑换金币
@check_login
def cash_gold(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    username = dict['username']
    dic = json.loads(str(request.GET['model']))
    gold = int(dic["godNum"])
    agent = Agent_user.objects.get(id=agent_id)
    if agent.gold < gold:
        return JsonResponse({'code': 103, 'data': '金币不足！'})
    agent.gold -= gold
    agent_charge = Agent_charge()
    agent_charge.agent_id = agent_id
    agent_charge.charge_src_agent = agent_id
    agent_charge.charge_num = -gold
    #9代表申请兑换金币并未兑换 10 表示兑换完成
    agent_charge.charge_type = 9
    agent.save()
    agent_charge.save()

    # agent_charge = Agent_charge()
    # agent_charge.agent_id = id
    # agent_charge.charge_src_agent = agent_id
    # agent_charge.charge_num = num
    # agent_charge.charge_type = 8
    # agent_charge.save()

    return JsonResponse({'code': 20000, 'data': agent.gold})

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

@check_login
def change_password(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    password = request.GET['pwd']
    agent = Agent_user.objects.get(id=agent_id)
    agent.password = password

    state = 1
    try:
        agent.save()
    except:
        state = 0
    data = {"state": state}
    return JsonResponse({'code': 20000, 'data': data})

@check_login
def delete_agent(request):
    delegate_id = int(str(request.GET['id']))
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    agent_name = dict['username']
    if agent_name == 'admin':
        obj = Agent_user.objects.get(id=delegate_id)
        obj.delete()
        return JsonResponse({'code': 20000})
    else:
        return JsonResponse({'code': 2000, 'data': '删除失败！'})




