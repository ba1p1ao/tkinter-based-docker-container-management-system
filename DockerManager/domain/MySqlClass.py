#!/usr/bin/env python3
# @Time : 2023/03/17 0017 11:34
# @Author : cui shi yuan
# @File : MySqlClass.py
import pymysql
import re
from tkinter import messagebox
from pymysql.converters import escape_string


class MySqlClass:
    def __init__(self, host, user, passwd, database):
        self.db = pymysql.connect(host=host, user=user, password=passwd, database=database)
        self.cur = self.db.cursor(cursor=pymysql.cursors.DictCursor)

    def __operate(self, sql, args):
        try:
            sql_new = self.__sanitize_sql(sql)
            args_new = self.__sanitize_args(args)
        except Exception as e:
            messagebox.showwarning(title='创建失败', message='输入的信息有敏感词汇')
        else:
            self.cur.execute(sql_new, args_new)
            self.db.commit()

    def __sanitize_sql(self, sql):
        # 去除SQL语句的注释
        sql = re.sub(r'--.*', '', sql)
        # 去掉SQL语句中的分号
        sql = sql.strip().rstrip(';')
        return sql

    def __sanitize_args(self, args):
        # 转义参数中的特殊字符
        sanitized_args = []
        for arg in args:
            if isinstance(arg, str):
                arg = escape_string(arg)
            sanitized_args.append(arg)
        return tuple(sanitized_args)

    def query(self, sql, *args):
        try:
            print(sql)
            print(args)
            sql_new = self.__sanitize_sql(sql)
            args_new = self.__sanitize_args(args)
            print(args_new)
            return bool(self.cur.execute(sql_new, args_new))
        except Exception as e:
            messagebox.showwarning(title='创建失败', message='输入的信息有敏感词汇')

    def getAll(self, sql, *args):
        try:
            sql_new = self.__sanitize_sql(sql)
            args_new = self.__sanitize_args(args)
            self.cur.execute(sql_new, args_new)
            return self.cur.fetchall()
        except Exception as e:
            messagebox.showwarning(title='创建失败', message='输入的信息有敏感词汇')

    def getOne(self, sql, *args):
        try:
            sql_new = self.__sanitize_sql(sql)
            args_new = self.__sanitize_args(args)
            self.cur.execute(sql_new, args_new)
            return self.cur.fetchall()
        except Exception as e:
            messagebox.showwarning(title='创建失败', message='输入的信息有敏感词汇')

    def insertData(self, sql, *args):
        self.__operate(sql, args)

    def deleteData(self, sql, *args):
        self.__operate(sql, args)

    def updateData(self, sql, *args):
        self.__operate(sql, args)

    def __del__(self):
        self.cur.close()
        self.db.close()


if __name__ == '__main__':
    msc = MySqlClass('192.168.10.101', 'root', '123', 'testdb')
    print(msc.query("select * from user where %s = %s", 'name', 'cui'))
    # print(msc.getAll("select * from user"))
