#!/usr/bin/env python3
# @Time : 2023/04/20 0020 14:39
# @Author : cui shi yuan
# @File : EmailSystem.py


import ConnectShell


class EmailSystem:
    def __init__(self):
        self.connect = ConnectShell.ConnectShell("192.168.10.121", 'root', '123', '22')

    def send(self, title, body, dest_mail):
        self.connect.commit("echo %s | mail -s %s %s" % (body, title, dest_mail))


if __name__ == '__main__':
    es = EmailSystem()
    es.send('验证码', '938722', '1302968967@qq.com')