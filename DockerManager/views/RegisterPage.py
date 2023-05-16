#!/usr/bin/env python3
# @Time : 2023/03/20 0020 21:33
# @Author : cui shi yuan
# @File : RegisterPage.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from ttkbootstrap.validation import add_regex_validation
import hashlib
import re
import pymysql
from utils import FunctionClass
from views import LoginPage
from domain import MySqlClass


class RegisterPage(ttk.Frame):
    msc = MySqlClass.MySqlClass('192.168.10.101', 'root', '123', 'testdb')

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("注册")
        self.pack()
        self.createWidget()

    def createWidget(self):
        ttk.Label(self).grid(row=0, column=0)
        self.username = ttk.StringVar()
        self.password1 = ttk.StringVar()
        self.password2 = ttk.StringVar()
        self.email = ttk.StringVar()
        ttk.Label(self, text='账号: ').grid(row=1, column=1)
        ttk.Entry(self, textvariable=self.username).grid(row=1, column=2)
        ttk.Label(self, text='密码: ').grid(row=2, column=1, pady=10)
        ttk.Entry(self, textvariable=self.password1, show='*').grid(row=2, column=2)
        ttk.Label(self, text='确认密码: ').grid(row=3, column=1, pady=10)
        ttk.Entry(self, textvariable=self.password2, show='*').grid(row=3, column=2)
        ttk.Label(self, text='邮箱: ').grid(row=4, column=1, pady=10)
        input_email = ttk.Entry(self, textvariable=self.email)
        input_email.grid(row=4, column=2)
        add_regex_validation(input_email, r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        ttk.Button(self, text='提交', bootstyle=SUCCESS,
                   command=self.createUser).grid(row=5, column=1, pady=10)
        ttk.Button(self, text='清空', bootstyle=WARNING,
                   command=self.clear).grid(row=5, column=2, padx=30)
        ttk.Button(self, text='返回', bootstyle=DANGER,
                   command=self.back).grid(row=5, column=3, padx=30)

    def back(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        LoginPage.LoginPage(self.master)

    def createUser(self):
        username = self.username.get()
        password1 = self.password1.get()
        password2 = self.password2.get()
        email = self.email.get()
        if username == '' or password1 == '' or password2 == '' or email == '':
            messagebox.showwarning(title='创建失败', message='输入的信息不能为空')
        elif self.msc.query("select * from user where name = %s", username):
            self.username.set('')
            messagebox.showwarning(title='创建失败', message='用户已存在')
        elif password1 == '':
            messagebox.showwarning(title='创建失败', message='密码不能为空')
        elif password1 != password2:
            self.password1.set('')
            self.password2.set('')
            messagebox.showwarning(title='创建失败', message='两次密码输入的不相同')
        elif not self.isEmailValid(email):
            messagebox.showwarning(title='创建失败', message='邮箱格式不合法')
        else:
            passwordmd5 = hashlib.md5(password1.encode('utf-8')).hexdigest()
            self.msc.insertData("insert into user values(%s, %s, %s)", username, passwordmd5, email)
            messagebox.showwarning(title='成功', message='创建成功')
            for widget in self.master.winfo_children():
                widget.destroy()
            LoginPage.LoginPage(self.master)

    def isEmailValid(self, email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return bool(re.fullmatch(regex, email))

    def clear(self):
        self.username.set('')
        self.password1.set('')
        self.password2.set('')
        self.email.set('')


if __name__ == '__main__':
    root = ttk.Window("注册", "superhero", resizable=(False, False))
    rp = RegisterPage(root)
    rp.mainloop()
