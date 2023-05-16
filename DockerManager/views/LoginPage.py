#!/usr/bin/env python3
# @Time : 2023/03/20 0020 21:07
# @Author : cui shi yuan
# @File : LoginPage.py
# from tkinter import *
from tkinter import messagebox
import hashlib
from views import RegisterPage, UpdatePasswdPage, MainPage
from domain import MySqlClass
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from utils import ConnectShell, FunctionClass



class LoginPage(ttk.Frame):
    msc = MySqlClass.MySqlClass('192.168.10.101', 'root', '123', 'testdb')

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.geometry('600x400+700+300')

        self.master.title("登录")
        self.createWidget()

    def createWidget(self):

        ttk.Label(self.master, text="欢迎登录", font=("Microsoft YaHei", 25)).place(x=220, y=20)
        # 创建其他组件
        self.username = ttk.StringVar(value="")
        self.password = ttk.StringVar(value="")
        self.hostip = ttk.StringVar(value="")
        self.port = ttk.StringVar(value="")
        ttk.Label(self.master, text='账号: ').place(x=180, y=105)
        ttk.Entry(self.master, textvariable=self.username).place(x=240, y=100)

        ttk.Label(self.master, text='密码: ').place(x=180, y=165)
        ttk.Entry(self.master, textvariable=self.password, show='*').place(x=240, y=160)

        ttk.Label(self.master, text='主机ip: ').place(x=100, y=225)
        ttk.Entry(self.master, textvariable=self.hostip, width=17).place(x=180, y=220)

        ttk.Label(self.master, text='端口号: ').place(x=380, y=225)
        ttk.Entry(self.master, textvariable=self.port, width=5).place(x=460, y=220)

        ttk.Button(self.master, bootstyle="success", text='登录', width=4,
                   command=lambda: self.login(self.username.get(), self.password.get())).place(x=170, y=300)
        ttk.Button(self.master, text='注册', width=4,
                   command=self.registerUser).place(x=270, y=300)
        ttk.Button(self.master, text='修改密码', width=8,
                   command=self.updatePasswd).place(x=370, y=300)

    def registerUser(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        RegisterPage.RegisterPage(self.master)

    def updatePasswd(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        UpdatePasswdPage.UpdatePasswdPage(self.master)

    def login(self, username, password):
        ip = self.hostip.get()
        port = self.port.get()
        passwordmd5 = hashlib.md5(password.encode('utf-8')).hexdigest()
        if username == '' or password == '' or ip == '' or port == '':
            messagebox.showwarning(title='登录失败', message='输入的信息不能为空')
        elif not FunctionClass.isOnline(ip, port):
            messagebox.showwarning(title='登录失败', message='远程服务器无法连接')
        elif self.msc.query("select * from user where name = %s and passwd = %s", username, passwordmd5):
            print('登录成功')
            with open('../data/username.txt', 'w') as f:
                f.writelines(username)
            hostip = self.hostip.get()
            port = self.port.get()
            with open('../data/hostip.txt', 'w') as f:
                f.write(hostip + ":" + port)
            for widget in self.master.winfo_children():
                widget.destroy()
            MainPage.MainPage(self.master)
        else:
            messagebox.showwarning(title='登录失败', message='账号或密码错误')


if __name__ == '__main__':
    app = ttk.Window("登录", "superhero", resizable=(False, False))
    LoginPage(app)
    app.mainloop()
