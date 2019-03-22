import socket
import struct
import json
import urllib.request
import urllib.parse
import logging
import redis
from configparser import ConfigParser
from summer_admin import settings

# 日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)

# 配置 服务器端口
config = ConfigParser()
config.read(settings.BASE_DIR + '/config.conf')
ip = config.get('robot', 'gameIp')
port = config.get('robot', 'loginServerPort')

# 机器人管理账号
manager_account = 'managerRobot'
manager_password = 'managerRobot'

# room_type
room_type = {
    '1': '''{"service":"mahjongRoomService","method":"createRoomButNotInRoom","params":{"userId":"0",
    "modeTotal":"15","mode":"1024","multiple":"1","gameNumber":"8","personNumber":"4","gameType":"LQ",
    "roomType":"1"}} '''

}


def create_room(account, password, game_type):
    """
    创建房间
    :param account:
    :param password:
    :param game_type:
    :return:
    """

    # 登录
    login_code, s = __login(account, password)

    result = {'code': -1}
    # 登录gate成功
    if login_code == 0:
        # 发送创建房间
        try:
            create_str = config.get('roomType', game_type)
        except:
            return json.dumps(result)

        json_node = json.loads(create_str)

        create_rtn = __send_msg(s, json_node)
        result = create_rtn
        logger.debug("创建房间返回: " + create_rtn)

    s.close()
    return result


def send_message(account, password, message):
    """
    发送消息
    :param account:
    :param password:
    :param game_type:
    :return:
    """

    # 登录
    login_code, s = __login(account, password)

    result = {'code': -1}
    # 登录gate成功
    if login_code == 0:
        # 发送创建房间
        # try:
        #     create_str = config.get('roomType', game_type)
        # except:
        #     return json.dumps(result)

        json_node = json.loads(message)

        create_rtn = __send_msg(s, json_node)
        result = create_rtn
        logger.debug("发送消息返回: " + create_rtn)

    s.close()
    return result




def get_room_info(room_id):
    """
    获得房间信息
    :param room_id:
    :return:
    """
    # 登录 以管理账号登录
    login_code, s = __login(manager_account, manager_password)

    result = json.dumps({'code':'-1'})
    # 登录gate成功
    if login_code == 0:
        # 发送获得房间信息
        req = {'service': 'userService', 'method': 'getRoomInfo', 'params': {'roomId': room_id}}

        result = create_rtn = __send_msg(s, req)
        logger.debug("获得房间信息: " + create_rtn)

    s.close()
    return result


def __login_game(account, password):
    """
    登录游戏账号服务器
    :param account:
    :param password:
    :return:
    """
    data = {'account': account, 'password': password}

    url_parame = urllib.parse.urlencode(data)

    request = urllib.request.Request("http://" + ip + ":" + port + "/login?" + url_parame,
                                     bytes(json.dumps(data), 'utf8'),
                                     method='GET')

    response = urllib.request.urlopen(request)

    the_page = response.read().decode()
    logging.debug("登录账号服务器返回: " + the_page)
    param = json.loads(the_page)
    userid = param['params']['userId']
    token = param['params']['token']
    logging.debug('登录玩家 userid: ' + str(userid) + ' token: ' + token)
    return param['params']
    # print(the_page)


def __login_gate(socket_, user_id, token):
    """
    登录gate服务器
    :param socket_:
    :param user_id:
    :param token:
    :return:
    """
    msg = {'service': 'gateService', 'method': 'login', 'params': {'userId': user_id, 'token': token}}

    rtn = __send_msg(socket_, msg)
    logging.debug("登录gate的返回: " + rtn)
    rtn_json = json.loads(rtn)
    code = rtn_json['code']
    logging.debug("登录gate的返回code: " + str(code))
    return code


def __send_msg(socket, msg):
    """
    发送消息
    :param socket:
    :param msg:
    :return:
    """

    msg_str = msg
    if type(msg) != 'str':
        msg_str = json.dumps(msg)

    msg_bytes = bytearray(msg_str, 'utf-8')

    msg_bytes_len = len(msg_bytes)
    # 数字转字符数组
    msg_bytes_len_bytes = bytearray(struct.pack(">I", msg_bytes_len))
    msg_result = msg_bytes_len_bytes + msg_bytes

    socket.sendall(msg_result)

    re = socket.recv(3096)

    return bytearray(re)[4:].decode()


def __login(account, password):
    """
    登录
    :param account:
    :param password:
    :return: 返回登录码 和 socket医用
    """
    parms = __login_game(account, password)

    # host
    host = parms['domain']
    if host == "":
        host = parms['ip']

    # socket
    s = __get_socket(host, parms['port'])

    login_code = __login_gate(s, parms['userId'], parms['token'])
    return login_code, s


def __get_socket(host, port):
    """
    获得socket
    :param host:
    :param port:
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s


def main():
    to = r.get('user_token:1').decode()
    print(to)
    # create_room('888', '111', 1)
    # get_room_info('888', '111','565224')


if __name__ == '__main__':
    main()
