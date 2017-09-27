from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from summer_admin.rpc.gameIdl.GameRPCNew import *
from summer_admin.rpc.gameIdl.ttypes import *


def main():
    transport = TSocket.TSocket('localhost', 9090)

    # Buffering is critical. Raw sockets are very slow
    # transport = TTransport.TBufferedTransport(transport)
    transport = TTransport.TFramedTransport(transport)

    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    # Create a client to use the protocol encoder


    # Connect!
    transport.open()

    client = Client(protocol)

    print(client.getUserInfo(1))


def get_client():
    transport = TSocket.TSocket('localhost', 9090)

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