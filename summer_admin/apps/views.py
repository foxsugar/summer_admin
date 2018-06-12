import datetime
import json
import uuid

from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from summer_admin.apps.models import *
from summer_admin.robot.robot import config
from summer_admin.rpc.rpc import *


TIME_OUT = 60 * 60 * 2


def check_login(func):
    """
    检测登录装饰器
    """

    def wrapper(req):
        print(req)
        x_token = req.META['HTTP_X_TOKEN']
        print(x_token)
        agent = cache.get(x_token)
        if agent is None:
            return JsonResponse({'code': 50014, 'message': '请登录'})
        else:
            return func(req)

    return wrapper


@csrf_exempt
def login(request):
    # test_mongo()
    """A view of all bands."""
    data = json.loads(request.body.decode())
    # print(dict(request.body.decode()))
    username = data['username']
    password = data['password']
    users = Agent_user.objects.filter(username=username).filter(password=password)
    if users.values().count() > 0:
        user = users.values()[0]
        # 放入缓存
        user_cache = {'id': user['id'], 'level': user['level'], 'username': user['username']}
        token = uuid.uuid4().hex
        cache.set(token, user_cache, TIME_OUT)
        result = {'code': 20000, 'data': {'token': token}}
        return JsonResponse(result)
    else:
        return JsonResponse({'code': 2000, 'data': '账户密码错误'})


@check_login
def get_info(request):
    """获得用户信息"""

    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    username = dict['username']

    roles = None
    if username == 'admin':
        roles = ['admin']
    else:
        roles = ['delegate']

    array = Agent_user.objects.filter(id=agent_id)
    au = array[0]

    data = {'name': username, 'role': roles, 'money': au.money,
            'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'}
    return JsonResponse({'code': 20000, 'data': data})


@check_login
def agent_list(request):
    """代理列表"""
    page = int(str(request.GET['page']))
    size = int(str(request.GET['size']))
    index_left = (page - 1) * size
    index_right = page * size

    # table_data = list(Agent_user.objects.values()[index_left:index_right])

    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    agent_name = dict['username']

    array = None
    if agent_name == 'admin':
        array = Agent_user.objects.all()
    else:
        array = Agent_user.objects.filter(parent_id=agent_id)
    # array = Agent_user.objects.filter((Agent_user(parent_id=agent_id) | Agent_user(id=a)))
    table_data = list(array.values()[index_left:index_right])
    total_page = len(table_data)

    td = []
    for t in table_data:
        td.append(agent2vo(t))

    total_page = Agent_user.objects.count()

    data = {'tableData': td, 'totalPage': total_page}

    return JsonResponse({'code': 20000, 'data': data})


@check_login
def agent(request):
    param = json.loads(str(request.GET['agentForm']))
    # param['invite_code'] = 'in'
    param['level'] = 0
    param['parentId'] = 0
    param['idCard'] = "000000000000000000"
    param['area'] = '1'
    param['address'] = '1'
    param['payDeduct'] = 0
    param['shareDeduct'] = 0
    param['parentPayDeduct'] = 0
    param['parentShareDeduct'] = 0
    param['email'] = '1@qq.com'
    param['cell'] = '11111111111'
    # param['invite_code'] = '0'
    # param['invite_code'] = '0'
    param['realName'] = '0'
    method = request.method

    array = Agent_user.objects.filter(username=param['username'])

    print(len(array))
    if len(array) != 0:
        return JsonResponse({'code': 100, 'data': '该用户名已存在'})

    # 添加代理
    if method == "POST":
        create_agent_user(param, request)

        print("--")
        return JsonResponse({'code': 20000, 'data': param})


@check_login
def agent_charge_gold(request):
    x_token = request.META['HTTP_X_TOKEN']
    dict = cache.get(x_token)
    slf_name = dict["username"]
    slf_id = dict["id"]

    array = Agent_user.objects.filter(id=slf_id)
    t_data = list(array.all())
    agent_user = t_data[0]

    """代理充值"""
    param = json.loads(str(request.GET['chargeForm']))
    id = param['id']
    num = param['gold_num']
    isadd = None

    try:
        isadd = param['isadd']
    except:
        isadd = 1

    if isadd == 0:
        num = -num;

    if agent_user.gold < num:
        str1 = None
        if isadd:
            str1 = "充值失败"
        else:
            str1 = "减值失败"
        return JsonResponse({'code': 100, 'data': '充值失败'})

    agent = Agent_user.objects.get(id=id)
    agent.gold += num
    agent.save()

    if slf_name != 'admin':
        agent_user.gold -= num
        agent_user.save()

    # int
    # WX = 1;
    # int
    # ZFB = 2;
    # int
    # SHARE = 3;
    # int
    # CHARGE_CARD = 4;
    # int
    # BIND_REFERRER = 5;
    # int
    # AGENT = 7;



    level = dict["level"]
    agent_id = dict['id']
    agent_charge = Agent_charge()
    agent_charge.agent_id = id
    agent_charge.charge_src_agent = agent_id
    agent_charge.charge_num = num
    agent_charge.charge_type = 8
    agent_charge.save()

    return JsonResponse({'code': 20000, 'data': agent.gold})

@check_login
def agent_charge(request):
    x_token = request.META['HTTP_X_TOKEN']
    dict = cache.get(x_token)
    slf_name = dict["username"]
    slf_id = dict["id"]

    array = Agent_user.objects.filter(id=slf_id)
    t_data = list(array.all())
    agent_user = t_data[0]

    """代理充值"""
    param  = json.loads(str(request.GET['chargeForm']))
    id = param['id']
    num = int(param['num'])

    #
    # if not ret:
    #     return JsonResponse({'code': 100, 'data': ' 下分失败'})

    if num >= 0:
        str1 = "充值失败"
    else:
        str1 = "减值失败"

    if agent_user.money < num:

        if agent_user.gold < num:
            str1 = None

            return JsonResponse({'code': 100, 'data': str1})
        return JsonResponse({'code': 100, 'data': str1})

    agent = Agent_user.objects.get(id=id)
    agent.money += num
    agent.save()

    if slf_name != 'admin':
        agent_user.money -= num
        agent_user.save()

    # int
    # WX = 1;
    # int
    # ZFB = 2;
    # int
    # SHARE = 3;
    # int
    # CHARGE_CARD = 4;
    # int
    # BIND_REFERRER = 5;
    # int
    # AGENT = 7;



    level = dict["level"]
    agent_id = dict['id']
    agent_charge = Agent_charge()
    agent_charge.agent_id = id
    agent_charge.charge_src_agent = agent_id
    agent_charge.charge_num = num
    agent_charge.charge_type = 7
    agent_charge.save()

    return JsonResponse({'code': 20000, 'data': agent.money})

@check_login
def agent_upGoal(request):
    param = json.loads(str(request.GET['chargeForm']))
    uid = int(param['id'])
    gold = int(param['goal'])
    user = Users.objects.get(id=uid)

    rpc_client = get_client()
    o = Order(userId=uid, num=gold, type=ChargeType.gold, agentId=1)
    rtn = rpc_client.charge(o)
    if rtn == 0:
        return JsonResponse({'code': 20000, 'data': user.gold + gold})
    else:
        return JsonResponse({'code': 100, 'data': '下分成功'})

@check_login
def agent_downGoal(request):
    param = json.loads(str(request.GET['chargeForm']))
    uid = int(param['id'])
    gold = int( param['goal'])
    user = Users.objects.get(id=uid)
    rpc_client = get_client()
    order = Order(userId=uid, num=-gold, type=ChargeType.gold, agentId=1)
    rtn = rpc_client.charge(order)
    if rtn == 0:
        return JsonResponse({'code': 20000, 'data': user.gold - gold})
    else:
        return JsonResponse({'code': 100, 'data': ' 下分失败'})


@check_login
def constant(request):
    con = Constant.objects.filter(id=1).values()[0]

    return JsonResponse({'code': 20000, 'data': con})


@check_login
def constant_update(request):
    param = json.loads(str(request.GET['constantForm']))
    constant = Constant.objects.get(id=1)
    constant.init_money = param['init_money']
    constant.apple_check = param['apple_check']
    constant.download = param['download']
    constant.marquee = param['marquee']
    constant.version_of_android = param['version_of_android']
    constant.version_of_ios = param['version_of_ios']
    constant.apple_check = param['apple_check']
    category = config.get('robot', 'gameCategory')
    if category == 'bcbm':
        constant.access_code = param['access_code']
    constant.save()

    # 刷新游戏服务器数据
    client = get_client()
    # 调用这个是为了刷新服务器内存
    client.getBlackList()
    # client.modifyAndroidVersion(constant.version_of_android)
    return JsonResponse({'code': 20000, 'data': 'ok'})


def agent2vo(agent):
    """代理显示"""
    return {
        'id': agent['id'],
        'username': agent['username'],
        'password': agent['password'],
        'invite_code': agent['invite_code'],
        'realName': agent['real_name'],
        'level': agent['level'],
        'parentId': agent['parent_id'],
        'email': agent['email'],
        'createTime': agent['create_time'],
        'idCard': agent['id_card'],
        'cell': agent['cell'],
        'area': agent['area'],
        'address': agent['address'],
        'money': agent['money'],
        'gold': agent['gold'],
        'payDeduct': agent['pay_deduct'],
        'shareDeduct': agent['share_deduct'],
        'parentPayDeduct': agent['parent_pay_deduct'],
        'parentShareDeduct': agent['parent_share_deduct'],
    }


def create_agent_user(agent, request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    agent_name = dict['username']
    """创建代理"""
    user = Agent_user()
    data = agent
    user.username = data['username']
    user.password = data['password']
    user.invite_code = data['invite_code']
    user.real_name = data['realName']
    user.level = data['level']
    user.parent_id = agent_id
    user.email = data['email']
    user.create_time = datetime.datetime.now()
    user.id_card = data['idCard']
    user.cell = data['cell']
    user.area = data['area']
    user.address = data['address']
    user.money = 0
    user.gold = 0
    user.pay_deduct = data['payDeduct']
    user.share_deduct = data['shareDeduct']
    user.parent_pay_deduct = data['parentPayDeduct']
    user.parent_share_deduct = data['parentShareDeduct']
    # 保存
    user.save()





