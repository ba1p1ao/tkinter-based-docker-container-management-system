#!/usr/bin/env python3
# @Time : 2023/04/20 0020 22:40
# @Author : cui shi yuan
# @File : FunctionClass.py
import re
import socket


def isEmailValid(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return bool(re.fullmatch(regex, email))


def isOnline(ip, port):
    # 创建socket对象
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 设置超时时间为5秒
    sock.settimeout(5)
    try:
        # 尝试连接远程虚拟机
        result = sock.connect_ex((ip, int(port)))
        # 判断连接是否成功
        return result == 0
    except socket.error as e:
        print("Error - socket error occurred:", e)
    finally:
        # 关闭socket连接
        sock.close()
