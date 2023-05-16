#!/usr/bin/env python3
# @Time : 2023/04/20 0020 15:28
# @Author : cui shi yuan
# @File : UpdatePasswdPage.py
import hashlib
import sys
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import random
import re

from views import LoginPage
from domain import MySqlClass
from utils import EmailSystem


class UpdatePasswdPage(ttk.Frame):
    msc = MySqlClass.MySqlClass('192.168.10.101', 'root', '123', 'testdb')
    mycode = ''
    isViewPasswd = False

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("修改密码")
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        ttk.Label(self).grid(row=0, column=0)
        self.username = ttk.StringVar()
        self.email = ttk.StringVar()
        self.code = ttk.StringVar()
        self.password1 = ttk.StringVar()
        self.password2 = ttk.StringVar()
        ttk.Label(self, text='账户: ').grid(row=1, column=1, pady=10)
        ttk.Entry(self, textvariable=self.username).grid(row=1, column=2, pady=10)
        ttk.Label(self, text='邮箱: ').grid(row=2, column=1, pady=10)
        ttk.Entry(self, textvariable=self.email).grid(row=2, column=2, pady=10)
        ttk.Button(self, text='获取验证码', command=self.getCode).grid(row=2, column=3, padx=10)
        ttk.Label(self, text='验证码: ').grid(row=3, column=1, pady=10)
        ttk.Entry(self, textvariable=self.code).grid(row=3, column=2)
        ttk.Label(self, text='密码: ').grid(row=4, column=1, pady=10)
        self.mm = ttk.Entry(self, textvariable=self.password1, show='*')
        self.mm.grid(row=4, column=2)
        self.showPasswdBtn = ttk.Button(self, text='显示密码', command=self.toggleViewPasswd)
        self.showPasswdBtn.grid(row=4, column=3)
        ttk.Label(self, text='确认密码: ').grid(row=5, column=1, pady=10)
        self.qrmm = ttk.Entry(self, textvariable=self.password2, show='*')
        self.qrmm.grid(row=5, column=2)
        ttk.Button(self, text='确认', bootstyle=SUCCESS,
                   command=self.updatePassword).grid(row=6, column=1, pady=10)
        ttk.Button(self, text='清空', bootstyle=WARNING,
                   command=self.clear).grid(row=6, column=2, padx=30)
        ttk.Button(self, text='返回', bootstyle=DANGER,
                   command=self.back).grid(row=6, column=3, padx=20)

    def isEmailValid(self, email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return True if re.fullmatch(regex, email) else False

    def toggleViewPasswd(self):
        self.isViewPasswd = not self.isViewPasswd
        if self.isViewPasswd:
            self.mm.config(show='')
            self.qrmm.config(show='')
            self.showPasswdBtn.config(text='隐藏密码')
        else:
            self.mm.config(show='*')
            self.qrmm.config(show='*')
            self.showPasswdBtn.config(text='显示密码')
        self.master.focus()  # 为了取消焦点从显示密码按钮上

    def updatePassword(self):
        username = self.username.get()
        password1 = self.password1.get()
        password2 = self.password2.get()
        code = self.code.get()
        if username == '' or password1 == '' or code == '' or code == '':
            messagebox.showwarning(title='更新失败', message='输入的信息不能为空')
        elif code != self.mycode:
            self.code.set('')
            messagebox.showwarning(title='更新失败', message='验证码不正确')
        elif password1 == '':
            messagebox.showwarning(title='更新失败', message='密码不能为空')
        elif password1 != password2:
            self.password1.set('')
            self.password2.set('')
            messagebox.showwarning(title='更新失败', message='两次密码输入的不相同')
        else:
            passwordmd5 = hashlib.md5(password1.encode('utf-8')).hexdigest()
            self.msc.insertData("update user set passwd = %s where name = %s", passwordmd5, username)
            messagebox.showwarning(title='成功', message='修改成功')
            self.destroy()
            LoginPage.LoginPage(self.master)

    def clear(self):
        self.username.set('')
        self.email.set('')
        self.code.set('')
        self.password1.set('')
        self.password2.set('')

    def back(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        LoginPage.LoginPage(self.master)

    def getCode(self):
        dest_email = self.email.get()
        username = self.username.get()
        print(username, dest_email)
        if not self.isEmailValid(dest_email):
            messagebox.showwarning(title='获取失败', message='邮箱格式不合法')
        elif not self.msc.query("select * from user where name = %s and email = %s", username, dest_email):
            messagebox.showwarning(title='获取失败', message="该用户邮箱不匹配")
        else:
            cs = EmailSystem.EmailSystem()
            title = "修改密码"
            self.mycode = str(random.randint(100000, 1000000))
            message = self.mycode
            print(title, message)
            cs.send(message, title, dest_email)


if __name__ == '__main__':
    root = ttk.Window("修改密码", "superhero", resizable=(False, False))
    UpdatePasswdPage(root)
    root.mainloop()
