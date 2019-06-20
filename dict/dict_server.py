"""
dict 服务端

功能：业务逻辑处理
模型：多进程　tcp 并发
"""

from socket import *
from multiprocessing import Process
import signal
import sys
from operation_db import *
from time import sleep

#全局变量
HOST = '0.0.0.0'
PORT = 8000
ADDR = (HOST, PORT)

#数据库对象
db = Database()


#注册处理
def do_register(c, data):
    tmp = data.split(' ')
    name = tmp[1]
    passwd = tmp[2]
    if db.register(name, passwd):
        c.send(b'OK')
    else:
        c.send(b"Fail")


#登录处理
def do_login(c, data):
    tmp = data.split(' ')
    name = tmp[1]
    passwd = tmp[2]
    if db.login(name, passwd):
        c.send(b'OK')
    else:
        c.send(b"Fail")

#############################################################


#查单词
def do_query(c, data):
    tmp = data.split(' ')
    name = tmp[1]
    word = tmp[2]

    db.insert_history(name, word)  #插入历史记录

    #找到返回解释，没找到返回None
    mean = db.query(word)
    if not mean:
        c.send("没有找到该单词".encode())
    else:
        msg = "%s : %s" % (word, mean)
        c.send(msg.encode())


#历史记录
def do_hist(c, data):
    name = data.split(" ")[1]
    r = db.history(name)
    if not r:
        c.send(b'Fail')
        return
    c.send(b'OK')

    for i in r:
        #i-->(name,word,time)
        msg = "%s   %-16s     %s" % i
        sleep(0.1)   #防止两个msg粘在一起，出现在同一行
        c.send(msg.encode())
    sleep(0.1)   #防止'##'和前面的记录粘在一行，从而无法执行退出操作。
    c.send(b'##')
    #粘包产生原因:
    # 1.TCP协议本身造成的,TCP为提高效率,若连续几次发送的数据都很少，通常TCP会把数据合成一包后一次发送出去。　
    # 2.接收方用户进程不及时接收数据，未能及时取走缓冲区内的包。


#接受客户端请求，分配处理函数
def request(c):
    db.create_cursor()  #生成游标
    while True:
        data = c.recv(1024).decode()
        if not data or data[0] == 'E':
            sys.exit()
        print(c.getpeername(), ":", data)
        if data[0] == "R":
            do_register(c, data)   #传入客户端连接套接字c，方便在函数中发送数据。
        elif data[0] == "L":
            do_login(c, data)
        elif data[0] == "Q":
            do_query(c, data)
        elif data[0] == "H":
            do_hist(c, data)

##########################################################################


#搭建网络
def main():
    #创建tcp 套接字
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(3)

    #处理僵尸进程
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    #循环等待客户端连接
    print("Listen the port 8000")
    while True:
        try:
            c, addr = s.accept()
            print("Connect from ", addr)
        except KeyboardInterrupt:
            s.close()
            db.close()
            sys.exit("服务端退出")
        except Exception as e:
            print(e)
            continue

        #为客户端创建子进程
        p = Process(target=request, args=(c,))
        p.daemon = True
        p.start()


if __name__ == "__main__":
    main()



















