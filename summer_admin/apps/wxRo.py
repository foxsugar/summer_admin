
import threading

# def run_wx():
#     itchat.auto_login()
#     itchat.run()
#
#
#
# @itchat.msg_register(itchat.content.TEXT,isGroupChat=True)
# def text_reply(msg):
#     # print(msg)
#     if msg['Type'] == 'Text':
#         print('msg : ' + msg.text)
#         # print("from user : " + msg.formUser)
#
#     # return msg.text
#
#
#
#
# itchat.auto_login(hotReload=True)
# itchat.run()

# instancePool = {}
#
#
#
#
#
#
# def start(request):
#     uid = str(request.GET['id'])
#     newInstance = itchat.new_instance()
#     instancePool[uid] = newInstance
#     newInstance.auto_login(hotReload=True, statusStorageDir=uid+'.pkl')
#
#     # newInstance.msg_register(itchat.content.TEXT,isGroupChat=True)
#     # newInstance.start_receiving(exitCallback=exitFun, getReceivingFnOnly=True)
#
#     @newInstance.msg_register(itchat.content.TEXT,isGroupChat=True)
#     def reply(msg):
#         print(msg.text)
#
#     t = threading.Thread(target=newInstance.run(), args=())
#
#     t.start()
#
#     return "请在手机确认登录"
#     # newInstance.run()
#
#
# def exitFun():
#     print("exit")


#
# def st(wxInstance):
#     @wxInstance.msg_register(itchat.content.TEXT, isGroupChat=True)
#     def reply(msg):
#         print(msg.text)


# @itchat.msg_register(itchat.content.TEXT,isGroupChat=True)
# def reply(msg):
#     print(msg.text)
#     # return msg.text