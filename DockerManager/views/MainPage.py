#!/usr/bin/env python3
# @Time : 2023/03/20 0020 22:34
# @Author : cui shi yuan
# @File : MainPage.py

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from domain import MyDockerManager, DockerMysql
import ViewsPage
import importlib
import inspect

mdm = MyDockerManager.MyDockerManager("192.168.10.101", "2375")


class MainPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("管理系统")
        self.master.geometry("900x650+500+300")
        self.createPage()
        self.createWidget()

    def createPage(self):
        self.FRAME = {
            "welcome": ViewsPage.WelcomePage,
            "query_container": ViewsPage.QueryContainerFrame,
            "create_container": ViewsPage.CreateContainerFrame,
            "delete_container": ViewsPage.DeleteContainerFrame,
            "update_container": ViewsPage.UpdateContainerFrame,
            "about_user": ViewsPage.AboutUserFrame,
            "about_author": ViewsPage.AboutAuthorFrame,
            "log": ViewsPage.LogFrame,
            "pull_image": ViewsPage.PullImageFrame,
            "delete_image": ViewsPage.DeleteImageFrame,
            "query_image": ViewsPage.QueryImageFrame,
            "terminal": ViewsPage.TerminalFrame,
            "backup": ViewsPage.BackupFrame,
            "import": ViewsPage.ImportFrame
        }

        self.frames = self.initialize_frames()
        self.frames['welcome'].pack()
        self.frames['welcome'].focus_force()

    def createWidget(self):

        importMenu = ttk.Menu(self, tearoff=0)
        importMenu.add_command(label="导入压缩包", command=self.showImport)
        importMenu.add_command(label="导入DockerFile", command=ViewsPage.ImportDockerFile)
        # 管理文件的菜单
        fileMenu = ttk.Menu(self, tearoff=0)
        fileMenu.add_cascade(label="导入", menu=importMenu)
        fileMenu.add_command(label="导出", command=self.showBackup)
        fileMenu.add_command(label="查看日志", command=self.showLog)
        fileMenu.add_command(label="同步数据库", command=self.syncDatabase)
        fileMenu.add_command(label="刷新", command=self.refresh)
        fileMenu.add_separator()
        fileMenu.add_command(label="退出", command=self.quit)

        # 管理image的子菜单
        imageMenu = ttk.Menu(self, tearoff=0)
        imageMenu.add_command(label="拉取", command=self.showPullImage)
        imageMenu.add_command(label="删除", command=self.showDeleteImage)
        imageMenu.add_command(label="查询", command=self.showQueryImage)

        # 管理container的子菜单
        containerMenu = ttk.Menu(self, tearoff=0)
        containerMenu.add_command(label="增加", command=self.showCreateContainer)
        containerMenu.add_command(label="删除", command=self.showDeleteContainer)
        containerMenu.add_command(label="修改", command=self.showUpdateContainer)
        containerMenu.add_command(label="查询", command=self.showQueryContainer)

        # 关于子菜单
        aboutMenu = ttk.Menu(self, tearoff=0)
        aboutMenu.add_command(label="帮助")
        aboutMenu.add_command(label="关于用户", command=self.showAboutUser)
        aboutMenu.add_command(label="关于作者", command=self.showAboutAuthor)

        # 创建主菜单
        mainMenu = ttk.Menu(self, takefocus=0, font=12)
        mainMenu.add_cascade(label="开始", menu=fileMenu)
        # mainMenu.add_separator()
        mainMenu.add_cascade(label="管理镜像", menu=imageMenu)
        mainMenu.add_cascade(label="管理容器", menu=containerMenu)
        mainMenu.add_cascade(label="关于", menu=aboutMenu)
        mainMenu.add_command(label="打开终端", command=self.showTerminal)

        self.master.config(menu=mainMenu)

    def initialize_frames(self, frame_name=None):
        frames = {}
        for name, FrameClass in self.FRAME.items():
            if name == frame_name and frame_name == 'terminal':
                frame = FrameClass(self.master, True)
            else:
                frame = FrameClass(self.master)
            frames[name] = frame
            frame.pack_forget()
        return frames

    def packForgetAll(self):
        for name, frame in self.frames.items():
            frame.pack_forget()

    def showFrame(self, frame_name):
        # 隐藏丢弃所有的frame
        for name, frame in self.frames.items():
            frame.pack_forget()
            # del函数删除类
            del frame

        if frame_name != 'terminal':
            self.frames['terminal'].pause_thread()
            self.frames = self.initialize_frames()
        else:
            self.frames = self.initialize_frames("terminal")
        # 显示对应的frame
        self.frames[frame_name].pack()

    def refresh(self):
        self.showFrame("welcome")

    def syncDatabase(self):
        DockerMysql.syncDocker()
        DockerMysql.syncImage()
        messagebox.showinfo(title='同步成功', message='同步数据库成功')

    def showQueryContainer(self):
        self.showFrame('query_container')

    def showCreateContainer(self):
        self.showFrame("create_container")

    def showDeleteContainer(self):
        self.showFrame("delete_container")

    def showUpdateContainer(self):
        self.showFrame("update_container")

    def showPullImage(self):
        self.showFrame("pull_image")

    def showDeleteImage(self):
        self.showFrame("delete_image")

    def showQueryImage(self):
        self.showFrame("query_image")

    def showAboutUser(self):
        self.showFrame("about_user")

    def showAboutAuthor(self):
        self.showFrame("about_author")

    def showLog(self):
        self.showFrame("log")

    def showTerminal(self):
        self.showFrame("terminal")

    def showBackup(self):
        self.showFrame("backup")

    def showImport(self):
        self.showFrame("import")


if __name__ == '__main__':
    root = ttk.Window('Docker Manager', "superhero", resizable=(False, False))
    MainPage(root)
    root.mainloop()
