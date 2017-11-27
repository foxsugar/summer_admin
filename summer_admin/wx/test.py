import itchat


def qrc():
    print("qrc")

if __name__ == '__main__':


    itchat.auto_login(qrCallback=qrc())

    itchat.send('Hello, filehelper', toUserName='filehelper')
    print("=================")