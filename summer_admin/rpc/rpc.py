from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from summer_admin.rpc.gameIdl.GameRPCNew import *
from summer_admin.rpc.gameIdl.ttypes import *
from  configparser import ConfigParser
from summer_admin import settings


def main():
    transport = TSocket.TSocket('39.104.125.77', 9090)
    #
    # # Buffering is critical. Raw sockets are very slow
    # # transport = TTransport.TBufferedTransport(transport)
    transport = TTransport.TFramedTransport(transport)
    #
    # # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    #
    # # Create a client to use the protocol encoder
    #
    #
    # # Connect!
    transport.open()
    #
    client = Client(protocol)
    # order = Order()
    # order.agentId = 1
    # order.id = 3
    # order.num = 100000
    # order.type = 1

    order = Order(userId=100074, num=100000, type=ChargeType.gold, agentId=0)
    client.charge(order=order)
    #
    # print(client.getUserInfo(1))

    # client = get_client()
    # order = Order()
    # order.agentId = 1
    # order.id = 1
    # order.num = 1
    # client.charge(order=order)


def get_client():
    config = ConfigParser()
    # co = config.read('E://workspace/summer_admin1/summer_admin/config.conf')
    config.read(settings.BASE_DIR + '/config.conf')
    ip = config.get('rpc', 'gameIp')
    port = config.get('rpc', 'gamePort')

    transport = TSocket.TSocket(ip, port)

    # Buffering is critical. Raw sockets are very slow
    # transport = TTransport.TBufferedTransport(transport)
    transport = TTransport.TFramedTransport(transport)

    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    # Create a client to use the protocol encoder


    # Connect!
    transport.open()

    client = Client(protocol)
    return client


if __name__ == '__main__':
    main()
