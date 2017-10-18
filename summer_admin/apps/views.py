import datetime
import json
import uuid

from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from summer_admin.apps.models import *

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
        user_cache = {'id': user['id'], 'level': user['level'], 'username' : user['username']}
        token = uuid.uuid4().hex
        cache.set(token, user_cache, TIME_OUT)
        result = {'code': 20000, 'data': {'token': token}}
        return JsonResponse(result)
    else:
        return JsonResponse({'code': 2000, 'data': '账户密码错误'})


@check_login
def get_info(request):
    """获得用户信息"""
    roles = ['admin']
    data = {'name': 'sun', 'role': roles,
            'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'}
    return JsonResponse({'code': 20000, 'data': data})


@check_login
def agent_list(request):
    """代理列表"""
    page = int(str(request.GET['page']))
    size = int(str(request.GET['size']))
    index_left = (page - 1) * size
    index_right = page * size

    table_data = list(Agent_user.objects.values()[index_left:index_right])
    td = []
    for t in table_data:
        td.append(agent2vo(t))

    total_page = Agent_user.objects.count()

    data = {'tableData': td, 'totalPage': total_page}

    return JsonResponse({'code': 20000, 'data': data})


@check_login
def agent(request):
    param = json.loads(str(request.GET['agentForm']))
    method = request.method

    # 添加代理
    if method == "POST":
        create_agent_user(param)
        return JsonResponse({'code': 20000, 'data': param})


@check_login
def agent_charge(request):
    """代理充值"""
    param = json.loads(str(request.GET['chargeForm']))
    id = param['id']
    num = param['num']
    agent = Agent_user.objects.get(id=id)
    agent.money += num
    agent.save()


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

    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)

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
def constant(request):
    con = Constant.objects.filter(id=1).values()[0]

    return JsonResponse({'code': 20000, 'data': con})


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


def create_agent_user(agent):
    """创建代理"""
    user = Agent_user()
    data = agent
    user.username = data['username']
    user.password = data['password']
    user.invite_code = data['invite_code']
    user.real_name = data['realName']
    user.level = data['level']
    user.parent_id = data['parentId']
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
