#!/usr/bin/env python3
# @Time : 2023/03/25 0025 22:50
# @Author : cui shi yuan
# @File : ViewsPage.py

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap import utility
from tkinter.filedialog import *
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.validation import add_regex_validation
from PIL import Image, ImageTk
from tkinter import messagebox, simpledialog
from domain import MyDockerManager, MySqlClass
import threading
import json
import winpty
import time
import os

with open("../data/hostip.txt") as f:
    string = f.readline().split(":")
    for i in string:
        print(i)
    # print(len(string))
    # print(string[0], string[1])
    hostip = string[0]
    port = string[1]

mdm = MyDockerManager.MyDockerManager(hostip, port)
msc = MySqlClass.MySqlClass(hostip, 'root', '123', 'testdb')


# 欢迎页面
class WelcomePage(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master)
        self.master = master
        self.pack()
        self.createWidget()

    def createWidget(self):
        # create a label with a welcome message
        welcome_label = ttk.Label(self, text="欢迎使用Docker容器管理系统", font=("Helvetica", 20))
        welcome_label.pack(pady=20)

        # create an image of a Docker container
        image = Image.open("../picture/20200701172759.png")
        image = image.resize((900, 550), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)

        # create a label to display the image
        image_label = ttk.Label(self, image=photo)
        image_label.image = photo
        image_label.pack()


class QueryContainerFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, padding=25)
        self.master = master
        self.containers = mdm.getAllDockers()
        self.pack()
        self.createWidget()

    def createWidget(self):
        titles = [
            {"text": "id", "stretch": False},
            {"text": "image", "stretch": True},
            {"text": "name"},
            {"text": "status"},
            {"text": "port"},
            {"text": "created"}
        ]

        dataList = []
        for container in self.containers:
            dataList.append((container['id'], container['image'], container['name'], container['status'],
                             container['ports'], container['created']))
        self.table = Tableview(
            master=self,
            paginated=True,
            coldata=titles,
            rowdata=dataList,
            searchable=True,
            bootstyle=PRIMARY,
            pagesize=10,
            height=20,
        )
        self.table.pack()
        self.table.autofit_columns()


class UpdateContainerFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, padding=25)
        self.master = master
        self.containers = mdm.getAllDockers()
        self.pack()
        self.createWidget()

    def createWidget(self):
        # 获取容器数据
        # 定义表格标题
        self.cols = ("id", "image", "name", "status", "port", "created")
        # 创建Treeview表格
        self.tree = ttk.Treeview(self, columns=self.cols, bootstyle=ttk.INFO, show=ttk.HEADINGS, height=20)
        self.tree.grid(row=0, column=0, sticky=ttk.NSEW)
        # 设置列宽和列名

        self.tree.column('id', anchor=ttk.CENTER, width=120)
        self.tree.column('image', anchor=ttk.CENTER, width=200)
        self.tree.column('name', anchor=ttk.CENTER, width=120)
        self.tree.column('status', anchor=ttk.CENTER, width=80)
        self.tree.column('port', anchor=ttk.CENTER, width=60)
        self.tree.column('created', anchor=ttk.CENTER, width=170)
        self.tree.heading('id', text='id')
        self.tree.heading('image', text='image')
        self.tree.heading('name', text='name')
        self.tree.heading('status', text='status')
        self.tree.heading('port', text='ports')
        self.tree.heading('created', text='created')
        # 添加数据
        for container in self.containers:
            self.tree.insert("", ttk.END, values=(
                container['id'], container['image'], container['name'], container['status'],
                container['ports'], container['created']))
        # 添加滚动条
        ysb = ttk.Scrollbar(self, orient=ttk.VERTICAL, command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient=ttk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        ysb.grid(row=0, column=1, sticky=ttk.NS)
        xsb.grid(row=1, column=0, sticky=ttk.EW)
        # 添加刷新按钮
        self.refresh_button = ttk.Button(self, text='刷新', command=self.refreshTable)
        self.refresh_button.grid(row=2, column=0, sticky=ttk.E)
        # 设置表格和滚动条在窗口大小变化时可以自适应
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.tree.bind("<Double-Button-1>", self.on_click)

        # 判断如果是数字就医数字的形式排序
        def sortKey(x):
            if x[0].isdigit():
                return int(x[0])
            return x[0]

        def treeviewSortColumn(tv, col, reverse):  # Treeview、列名、排列方式
            l = [(tv.set(k, col), k) for k in tv.get_children('')]
            # print(tv.get_children(''))
            l.sort(reverse=reverse, key=lambda x: sortKey(x))  # 排序方式
            for index, (val, k) in enumerate(l):  # 根据排序后索引移动
                tv.move(k, '', index)
                # print(k)
            tv.heading(col, command=lambda: treeviewSortColumn(tv, col, not reverse))  # 重写标题，使之成为再点倒序的标题

        for col in self.cols:
            self.tree.heading(col, text=col, command=lambda _col=col: treeviewSortColumn(self.tree, _col, False))

    def refreshTable(self):
        # 删除原有数据
        for i in self.tree.get_children():
            self.tree.delete(i)
        # 获取新的数据并添加到表格中
        containers = mdm.getAllDockers()
        for container in containers:
            self.tree.insert("", ttk.END, values=(
                container['id'], container['image'], container['name'], container['status'],
                container['ports'], container['created']))

    def on_click(self, event):
        # 获取选中行的值
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item)['values']
        container = {}
        for i, value in enumerate(values):
            container[self.cols[i]] = value
        # 创建新窗口
        self.update_window = ttk.Toplevel(self.master)
        self.update_window.title("更新容器")
        self.update_window.geometry("+800+500")

        # 在新窗口中添加控件
        ttk.Label(self.update_window, text="容器名：").grid(row=0, column=0, padx=5, pady=5)
        self.name = container['name']
        self.newname = ttk.StringVar(value=container['name'])
        ttk.Entry(self.update_window, width=20, textvariable=self.newname).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.update_window, text="状态：").grid(row=1, column=0, padx=5, pady=5)
        self.statusVar = tk.IntVar()
        self.statusVar.set(1 if container['status'] == "running" else 0)
        ttk.Checkbutton(self.update_window, variable=self.statusVar,
                        bootstyle="round-toggle").grid(row=1, column=1, padx=5, pady=5)

        confirm_button = ttk.Button(self.update_window, text="确定", command=self.update_container)
        confirm_button.grid(row=2, column=1, padx=5, pady=5)

    def update_container(self):
        # 获取输入框中的值
        name = self.name
        newname = self.newname.get()
        status = 'running' if self.statusVar.get() == 1 else 'exited'
        for container in self.containers:
            if newname == container['name'] and name != container['name']:
                messagebox.showwarning(title='修改失败', message='容器名已存在')
                self.update_window.focus_force()
                return

        # TODO: 更新容器信息的代码
        mdm.updateContainer(name, newname, status)
        self.refreshTable()
        # 关闭窗口
        self.update_window.destroy()


class CreateContainerFrame(ttk.Frame):
    """
           1、获取images列表，用户通过选择image来创建容器，不需要用户输入，使用下拉框实现
           2、用户输入自定义的docker名称
           3、
       """

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, padding=20)
        self.master = master
        self.images = mdm.getAllImages()
        self.pack()
        self.createWidget()

    def createWidget(self):
        self.image_name = ttk.StringVar(value='请选择镜像')
        self.container_name = ttk.StringVar()
        self.port = ttk.StringVar()

        form_frame = ttk.LabelFrame(master=self, text="请输入容器信息")
        form_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        form_frame_image = ttk.Frame(master=form_frame)
        form_frame_image.pack(fill=X, expand=YES, pady=5, padx=10)

        image_label = ttk.Label(master=form_frame_image, text="镜像名：", width=12)
        image_label.pack(side=LEFT, fill=X, expand=YES, anchor=E)
        image_list = ['请选择镜像']
        for image in self.images:
            image_list.append(image['id'] + ":" + image['name'] + ":" + image['tag'])

        image_combobox = ttk.Combobox(master=form_frame_image, values=image_list, textvariable=self.image_name,
                                      width=24)
        image_combobox.pack(side=LEFT, padx=5, fill=X, expand=YES)

        self.createFormEntry(form_frame, "容器名：", self.container_name)
        self.createButtonbox(form_frame)

    def createFormEntry(self, master, label, variable):
        form_field_container = ttk.Frame(master=master)
        form_field_container.pack(fill=X, expand=YES, pady=5, padx=10)
        form_field_label = ttk.Label(master=form_field_container, text=label)
        form_field_label.pack(side=LEFT, expand=YES, anchor=E, fill=X)

        form_input = ttk.Entry(master=form_field_container, textvariable=variable, width=20)
        form_input.pack(side=LEFT, padx=5, fill=X, expand=YES)

        add_regex_validation(form_input, r'^[a-zA-Z0-9_\.]*$')

        return form_field_container

    def createButtonbox(self, master):
        button_container = ttk.Frame(master=master)
        button_container.pack(fill=X, expand=YES, pady=(15, 10))

        cancel_btn = ttk.Button(
            master=button_container,
            text="Cancel",
            command=self.onCancel,
            bootstyle=DANGER,
            width=6,
        )

        cancel_btn.pack(side=RIGHT, padx=5)

        submit_btn = ttk.Button(
            master=button_container,
            text="Submit",
            command=self.onSubmit,
            bootstyle=SUCCESS,
            width=6,
        )

        submit_btn.pack(side=RIGHT, padx=5)

    def onSubmit(self):
        image_name = self.image_name.get()
        container_name = self.container_name.get()
        print(image_name, container_name)
        if image_name == '请选择镜像':
            messagebox.showwarning(title='创建错误', message='请选择镜像')
        else:
            # print(image_name, container_name)
            image_id = image_name.split(':')[0]
            mess = mdm.createDocker(image=image_id, name=container_name)
            if mess == 'success':
                messagebox.showinfo(title='创建成功', message='容器创建成功')
            elif mess == 'isExist':
                messagebox.showinfo(title='创建失败', message='容器已经存在')


    def onCancel(self):
        self.image_name.set('请选择镜像')
        self.container_name.set('')
        self.port.set('')


class DeleteContainerFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, padding=20)
        self.master = master
        self.containers = mdm.getAllDockers()
        self.pack()
        self.createWidget()

    def createWidget(self):
        self.container_name = ttk.StringVar(value="请选择容器")
        form_frame = ttk.LabelFrame(master=self, text="请选择要删除的容器名")
        form_frame.pack(fill=X, expand=YES, padx=10, pady=10)
        form_frame_container = ttk.Frame(master=form_frame)
        form_frame_container.pack(fill=X, expand=YES, pady=5, padx=10)

        container_label = ttk.Label(master=form_frame_container, text="镜像名：", width=12)
        container_label.pack(side=LEFT, expand=YES, anchor=E)

        self.container_combobox = ttk.Combobox(master=form_frame_container, values=self.get_containers(),
                                           textvariable=self.container_name,
                                           width=40, )
        self.container_combobox.pack(side=LEFT, fill=X, expand=YES, padx=5)

        button_container = ttk.Frame(form_frame)
        button_container.pack(fill=X, expand=YES, pady=(15, 10))

        cancel_btn = ttk.Button(
            master=button_container,
            text="删除",
            command=self.delete_container,
            bootstyle=DANGER,
            width=6,
        )
        cancel_btn.pack(side=RIGHT, padx=5)

    def get_containers(self):
        self.container_list = ["请选择容器"]
        self.containers = mdm.getAllDockers()
        for container in self.containers:
            self.container_list.append(container['id'] + ": " + container['name'])

        return self.container_list

    def delete_container(self):
        container_name = self.container_name.get()
        if container_name == '请选择容器':
            messagebox.showwarning(title='删除失败', message='请选择要删除的容器名')
        elif container_name not in self.container_list:
            messagebox.showwarning(title='删除失败', message="容器不存在")
        else:
            container_name = container_name.split(':')[0]
            print(container_name)
            if mdm.removeDockers(id=container_name):
                messagebox.showwarning(title='删除成功', message="删除成功")
            self.container_combobox['values'] = self.get_containers()
            self.container_name.set('请选择容器')


class PullImageFrame(ttk.Frame):
    """
        1、用户输入镜像的名称和镜像的版本号（默认latest）
        2、点击拉取按钮实现对镜像的拉取
        3、显示进度条功能，采用多线程的方式，将拉取过程加入子线程中，通过主线程不断地刷新界面，从而实现动态更新
    """

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, padding=(20, 10))
        self.master = master
        self.pack(fill=BOTH, expand=YES)
        self.createWidget()

    def createWidget(self):

        self.image_name = ttk.StringVar(value="")
        self.image_tag = ttk.StringVar(value="latest")
        instruction_text = "请输入镜像名称和版本号"
        instruction = ttk.Label(self, text=instruction_text, width=50)
        instruction.pack(fill=X, pady=10)
        self.createFormEntry("镜像名: ", self.image_name)
        self.createFormEntry("版本号: ", self.image_tag)
        self.createProgressbar()
        self.createButtonbox()

    def createFormEntry(self, label, variable):
        form_field_container = ttk.Frame(self)
        form_field_container.pack(fill=X, expand=YES, pady=5)

        form_field_label = ttk.Label(master=form_field_container, text=label)
        form_field_label.pack(side=LEFT, expand=YES, anchor=W)

        form_input = ttk.Entry(master=form_field_container, textvariable=variable)
        form_input.pack(side=LEFT, padx=5, fill=X, expand=YES)

        add_regex_validation(form_input, r'^[a-zA-Z0-9_\.]*$')

        return form_input

    def createProgressbar(self):
        progressbar_container = ttk.Frame(self)
        progressbar_container.pack(fill=X, expand=YES, pady=(15, 10))
        # 创建进度条
        self.progressbar = ttk.Progressbar(progressbar_container, orient=ttk.HORIZONTAL, length=500, mode='determinate')
        self.progressbar.pack(pady=10)

        self.percentage_label = ttk.Label(progressbar_container, text='0%')
        self.percentage_label.pack(pady=5)

    def createButtonbox(self):
        button_container = ttk.Frame(self)
        button_container.pack(fill=X, expand=YES, pady=(15, 10))

        cancel_btn = ttk.Button(
            master=button_container,
            text="重置",
            command=self.onCancel,
            bootstyle=DANGER,
            width=6,
        )

        cancel_btn.pack(side=RIGHT, padx=5)

        submit_btn = ttk.Button(
            master=button_container,
            text="拉取",
            command=self.onSubmit,
            bootstyle=SUCCESS,
            width=6,
        )

        submit_btn.pack(side=RIGHT, padx=5)

    def onSubmit(self):
        image_tag = self.image_tag.get()
        image_name = self.image_name.get()
        # 创建一个新的线程来执行拉取镜像的操作
        t = threading.Thread(target=self.pullImageThread, args=(image_name, image_tag))
        t.start()

    def pullImageThread(self, image_name, tag):
        messagebox.showinfo(title="提示", message="正在拉取请稍后")
        # 重置进度条
        self.progressbar['value'] = 0
        # 拉取镜像
        image = mdm.pullImageAPI(image_name, tag)
        # 显示进度条
        for line in image:
            if isinstance(line, bytes):
                line = line.decode('utf-8')  # 将bytes类型的字符串转换为str类型
            if 'progressDetail' in line:
                detail = json.loads(line)['progressDetail']  # 将str类型的JSON字符串转换为dict类型
                if 'total' in detail:
                    total = detail['total']
                    if 'current' in detail:
                        current = detail['current']
                        progress = int(current / total * 100)
                        self.progressbar['value'] = progress
                        self.percentage_label.config(text='{}%'.format(progress))
                        self.update_idletasks()

        # 拉取完成
        self.progressbar['value'] = 100
        messagebox.showinfo(title="拉取成功", message="镜像拉取成功")
    def onCancel(self):
        self.progressbar['value'] = 0
        self.percentage_label.config(text='0%')
        self.image_name.set('')
        self.image_tag.set('latest')


class DeleteImageFrame(ttk.Frame):
    """删除镜像"""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, padding=20)
        self.master = master
        self.images = mdm.getAllImages()
        self.pack()
        self.createWidget()

    def createWidget(self):
        self.image_name = ttk.StringVar(value="请选择镜像")
        form_frame = ttk.LabelFrame(master=self, text="请选择要删除的镜像名")
        form_frame.pack(fill=X, expand=YES, padx=10, pady=10)
        form_frame_container = ttk.Frame(master=form_frame)
        form_frame_container.pack(fill=X, expand=YES, pady=5, padx=10)

        images_label = ttk.Label(master=form_frame_container, text="镜像名：", width=12)
        images_label.pack(side=LEFT, expand=YES, anchor=E)

        self.image_combobox = ttk.Combobox(master=form_frame_container, values=self.get_images(),
                                           textvariable=self.image_name,
                                           width=40, )
        self.image_combobox.pack(side=LEFT, padx=5, fill=X, expand=YES)

        button_container = ttk.Frame(form_frame)
        button_container.pack(fill=X, expand=YES, pady=(15, 10))

        cancel_btn = ttk.Button(
            master=button_container,
            text="删除",
            command=self.delete_container,
            bootstyle=DANGER,
            width=6,
        )
        cancel_btn.pack(side=RIGHT, padx=5)

    def get_images(self):
        self.image_list = ["请选择镜像"]
        self.images = mdm.getAllImages()
        for image in self.images:
            self.image_list.append(f"{image['id']}:{image['name']}:{image['tag']}")

        return self.image_list

    def delete_container(self):
        image_name = self.image_name.get()
        if image_name == '请选择镜像':
            messagebox.showwarning(title='删除失败', message='请选择要删除的镜像名')
        elif image_name not in self.image_list:
            messagebox.showwarning(title='删除失败', message="镜像不存在")
        else:
            image_id = image_name.split(':')[0]
            print(image_name)
            if mdm.removeImages(id=image_id):
                messagebox.showinfo('删除成功', message="删除成功")
            else:
                messagebox.showwarning("删除失败", message="镜像正在被使用")

            self.image_combobox['values'] = self.get_images()
            self.image_name.set('请选择镜像')


class QueryImageFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, padding=25)
        self.master = master
        self.images = mdm.getAllImages()
        self.pack()
        self.createWidget()

    def createWidget(self):
        titles = [
            {"text": "id", "stretch": False},
            {"text": "name", "stretch": True},
            {"text": "version"},
            {"text": "created"},
            {"text": "size"},
        ]
        dataList = []
        for image in self.images:
            dataList.append((image['id'], image['name'], image['tag'], image['created'], image['size']))
        self.table = Tableview(
            master=self,
            paginated=True,
            coldata=titles,
            rowdata=dataList,
            searchable=True,
            bootstyle=PRIMARY,
            pagesize=10,
            height=20,
        )
        self.table.pack()
        self.table.autofit_columns()


class AboutUserFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master)
        self.master = master
        self.pack()
        self.createWidget()

    def createWidget(self):
        ttk.Label(self, text="cui").pack()


class AboutAuthorFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master)
        self.master = master
        self.pack()
        self.createWidget()

    def createWidget(self):
        ttk.Label(self, text='关于作品：是由tkinter制作').pack()
        ttk.Label(self, text='关于作者：csy').pack()


class LogFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, padding=10)
        self.filename = ttk.StringVar()
        self.pack(fill=BOTH, expand=YES)
        self.createWidget()

    def createWidget(self):
        self.createTextBox()
        options_frame = ttk.Frame(self)
        options_frame.pack(fill=X, expand=YES, padx=10, pady=10)
        options_label = ttk.Label(options_frame, text='请选择你要查看日志的容器')
        options_label.pack(side=LEFT, expand=NO, padx=10, pady=10, fill=X)
        self.container_list = ["请选择容器"]
        self.container_name = ttk.StringVar(value="请选择容器")
        self.containers = mdm.getAllDockers()
        for container in self.containers:
            self.container_list.append(container['id'] + ":" + container['name'])
        options_box = ttk.Combobox(master=options_frame, values=self.container_list,
                                   textvariable=self.container_name,
                                   width=40)
        options_box.pack(side=LEFT, expand=YES, padx=10, fill=X)
        browse_btn = ttk.Button(options_frame, text="查询", command=self.containerLogs)
        browse_btn.pack(side=RIGHT, fill=X, padx=(5, 0), pady=10)

    def containerLogs(self):

        container = self.container_name.get().split(":")
        mdm.logDocker(container)
        with open("E:/programming/pythonTest/DockerManager/logs/%s-%s.log" % (container[0], container[1])) as f:
            data = "".join(f.readlines())
        self.output.configure(state=NORMAL)
        self.output.delete(1.0, END)
        self.output.insert(END, data)
        self.output.configure(state=DISABLED)
        self.output.see(END)

    def createTextBox(self):
        text_frame = ttk.Frame(self)
        text_frame.pack(fill=X, expand=YES, pady=10, padx=10)
        self.output = ttk.Text(text_frame, state=DISABLED)
        self.output.pack(expand=True, fill=BOTH)


class TerminalFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, padding=(10, 20))
        self.master = master
        self.pack(fill=BOTH, expand=YES)
        self.is_run_thread = args
        self.createWidget()

    def pause_thread(self):
        self.is_run_thread = False

    def createWidget(self):
        instruction_text = "docker容器管理终端"
        instruction = ttk.Label(self, text=instruction_text, width=50)
        instruction.pack(fill=X, pady=10)
        self.createTextBox()
        self.createInputBox()
        # 启动一个伪终端进程，连接到远程主机
        self.term = winpty.PTY(rows=90, cols=200)
        self.term.spawn('ssh root@%s' % hostip)
        self.thread = threading.Thread(target=self.ptyThread, daemon=True)
        self.thread.start()

    def ptyThread(self):
        # print("pause")
        # print(self.is_run_thread)
        while self.is_run_thread:
            # 在新线程中读取终端输出
            data = self.term.read(10240)
            print('run')
            # 使用 master 和 winfo_exists 方法来检查父窗口是否存在
            if self.master and self.master.winfo_exists():
                self.output.configure(state=NORMAL)
                self.output.insert(END, str(data))
                self.output.configure(state=DISABLED)
                self.output.see(END)
            else:
                print('exit')
                exit()

    def createTextBox(self):
        text_frame = ttk.Frame(self)
        text_frame.pack(fill=X, expand=YES, pady=5)
        # 创建一个文本框来显示终端输出
        self.output = ttk.Text(text_frame, font=('Courier', 10), state=DISABLED)
        self.output.pack(expand=True, fill=BOTH)

    def createInputBox(self):
        input_frame = ttk.Frame(self)
        input_frame.pack(fill=X, expand=YES, pady=5)
        self.tip = ttk.Label(input_frame, text=">>", width=3)
        self.tip.pack(side=LEFT)
        # 创建一个文本框来显示终端输出
        self.input = ttk.Entry(input_frame)
        self.input.pack(side=LEFT, fill=X, expand=YES)
        self.input.focus_set()

        # 绑定事件处理函数
        self.input.bind("<Return>", self.send_command)

    def send_command(self, event):
        # 从输入框中获取命令，并发送到远程主机
        cmd = self.input.get() + '\n'
        self.term.write(cmd)
        self.input.delete(0, END)


class BackupFrame(ttk.Frame):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, padding=(10, 20))
        self.master = master
        self.remove_info = ''
        self.backup_containers_list = []
        self.backup_images_list = []
        self.containers = mdm.getAllDockers()
        self.images = mdm.getAllImages()
        self.pack(fill=BOTH, expand=YES)
        self.createWidget()

    def createWidget(self):
        self.createSelectFrame()
        self.create_results_view()
        self.createBackupButton()

    def createSelectFrame(self):
        labelFrame = ttk.LabelFrame(self, text="备份容器和镜像")
        labelFrame.pack(fill=X, expand=YES, padx=10, pady=5)

        noteBook = ttk.Notebook(labelFrame, width=600, height=100)
        noteBook.pack()

        select_frame_container = ttk.Frame(noteBook)
        select_frame_container.pack(fill=X, expand=YES, pady=10)

        label_container = ttk.Label(select_frame_container, text="容器名：")
        label_container.pack(side=LEFT, expand=YES, padx=10, pady=10)
        self.container_list = ["请选择容器"]
        for container in self.containers:
            self.container_list.append(container['id'] + ":" + container['name'])
        self.container_name = ttk.StringVar(value="请选择容器")
        combobox_container = ttk.Combobox(select_frame_container,
                                          values=self.container_list,
                                          textvariable=self.container_name)
        combobox_container.pack(side=LEFT, padx=10, expand=YES, fill=X)

        button_frame_image = ttk.Frame(noteBook)
        button_frame_image.pack(fill=X, expand=YES, pady=10)

        label_image = ttk.Label(button_frame_image, text="镜像名：")
        label_image.pack(side=LEFT, expand=YES, padx=10, pady=10)
        self.image_list = ["请选择镜像"]
        for image in self.images:
            self.image_list.append(image['id'] + ":" + image['name'] + "-" + image['tag'])
        self.image_name = ttk.StringVar(value="请选择镜像")
        combobox_image = ttk.Combobox(button_frame_image,
                                      values=self.image_list,
                                      textvariable=self.image_name)
        combobox_image.pack(side=LEFT, padx=10, expand=YES, fill=X)

        button_frame = ttk.Frame(labelFrame)
        button_frame.pack(fill=X, expand=YES, pady=10)

        submit_btn = ttk.Button(
            master=button_frame,
            text="添加",
            command=self.onSubmit,
            bootstyle=SUCCESS,
            width=6,
        )

        submit_btn.pack(side=RIGHT, padx=5)

        self.progressbar = ttk.Progressbar(self, orient=ttk.HORIZONTAL, length=500, mode='determinate')
        self.progressbar['value'] = 0
        self.progressbar.pack(fill=X, padx=10, pady=10)

        noteBook.add(select_frame_container, text='备份容器')
        noteBook.add(button_frame_image, text='备份镜像')

    def onSubmit(self):
        if self.container_name != "请选择容器":
            container_info = self.container_name.get().split(':')
            container_id = container_info[0]
            for l in self.containers:
                if container_id == l['id'] and container_id not in self.backup_containers_list:
                    self.resultview.insert('', END,
                                           values=[l['id'], l['name'], l['image'], l['status'], l['created'], '容器'])
                    self.backup_containers_list.append(container_id)
        if self.image_name != '请选择镜像':
            image_info = self.image_name.get().split(':')
            image_id = image_info[0]
            for l in self.images:
                if image_id == l['id'] and image_id not in self.backup_images_list:
                    self.resultview.insert('', END,
                                           values=[l['id'], l['name'] + "-" + l['tag'], '', '', l['created'], '镜像'])
                    self.backup_images_list.append(image_id)

    def create_results_view(self):
        """Add result treeview to labelframe"""
        self.resultview = ttk.Treeview(master=self,
                                       bootstyle=INFO,
                                       columns=[0, 1, 2, 3, 4, 5],
                                       show=HEADINGS)
        self.resultview.pack(fill=BOTH, expand=YES, pady=10, padx=10)

        # setup columns and use `scale_size` to adjust for resolution
        self.resultview.heading(0, text='ID', anchor=W)
        self.resultview.heading(1, text='名称', anchor=W)
        self.resultview.heading(2, text='镜像名称', anchor=W)
        self.resultview.heading(3, text='状态', anchor=W)
        self.resultview.heading(4, text='创建时间', anchor=W)
        self.resultview.heading(5, text='类别', anchor=W)
        self.resultview.column(column=0,
                               anchor=W,
                               width=utility.scale_size(self, 125),
                               stretch=False)
        self.resultview.column(column=1,
                               anchor=W,
                               width=utility.scale_size(self, 125),
                               stretch=False)
        self.resultview.column(column=2,
                               anchor=W,
                               width=utility.scale_size(self, 125),
                               stretch=False)
        self.resultview.column(column=3,
                               anchor=W,
                               width=utility.scale_size(self, 50),
                               stretch=False)
        self.resultview.column(column=4,
                               anchor=W,
                               width=utility.scale_size(self, 150),
                               stretch=False)
        self.resultview.column(column=5,
                               anchor=W,
                               width=utility.scale_size(self, 50))

        self.resultview.bind('<Button-3>', self.showPopup)
        self.popup_menu = ttk.Menu(self.master, tearoff=0)
        self.popup_menu.add_command(label='删除', command=self.deleteSelected)

    def showPopup(self, event):
        item = self.resultview.identify_row(event.y)
        if item:
            self.resultview.selection_set(item)
            self.popup_menu.post(event.x_root, event.y_root)

    def deleteSelected(self):
        selection = self.resultview.selection()
        for item in selection:
            self.resultview.delete(item)

    def createBackupButton(self):
        frame = ttk.Frame(self)
        frame.pack(fill=X, expand=YES, padx=10, pady=10)

        backup_button = ttk.Button(
            master=frame,
            text="备份",
            command=self.onBackup,
            bootstyle=SUCCESS,
            width=6,
        )

        backup_button.pack(side=RIGHT)

    def onBackup(self):
        if not self.resultview.get_children():
            messagebox.showwarning(title="备份失败", message="请添加要备份的数据")
        else:
            backup_tuple = []
            for item in self.resultview.get_children():
                values = self.resultview.item(item, 'values')
                backup_tuple.append((values[0], values[1]))

            path = askdirectory(title="Browse directory")
            self.backup_thread = threading.Thread(target=self.backup, args=(backup_tuple, path), daemon=True)
            self.backup_thread.start()

    def backup(self, backup_tuple, path):
        backup_containers_tuple = []
        backup_images_tuple = []
        if not path:
            messagebox.showwarning("警告", "路径不能为空")
            return

        for tu in backup_tuple:
            if tu[0] in self.backup_containers_list:
                backup_containers_tuple.append(tu)
            if tu[0] in self.backup_images_list:
                backup_images_tuple.append(tu)

        print(backup_containers_tuple)
        print(backup_images_tuple)

        total = len(backup_tuple)
        i = 0
        for ct in backup_containers_tuple:
            # print(bt)
            # 更新进度条
            if mdm.backupDocker(ct, path):
                self.progressbar['value'] = (i + 1) / total * 100
                self.progressbar.update()
                i += 1
        for it in backup_images_tuple:
            if mdm.backupImage(it, path):
                self.progressbar['value'] = (i + 1) / total * 100
                self.progressbar.update()
                i += 1

        if i == total:
            messagebox.showinfo(title="备份成功", message="备份成功")


class ImportFrame(ttk.Frame):

    def __init__(self, master):
        super().__init__(master, padding=(10, 20))
        self.master = master
        self.pack(fill=BOTH, expand=YES)
        self.createWidget()

    def createWidget(self):
        self.path_url = ttk.StringVar()
        self.import_path_list = set()
        self.createSelectFrame()
        self.create_results_view()
        self.createImportButton()

    def createSelectFrame(self):
        label_frame = ttk.LabelFrame(self, text="导入容器和镜像")
        label_frame.pack(fill=X, expand=YES, padx=10, pady=5, anchor=N)

        path_frame = ttk.Frame(label_frame)
        path_frame.pack(fill=X, expand=YES, padx=10, pady=10)

        path_label = ttk.Label(path_frame, text='路径')
        path_label.pack(side=LEFT, padx=10, pady=10)

        path_entry = ttk.Entry(path_frame, textvariable=self.path_url)
        path_entry.pack(side=LEFT, padx=10, pady=10, expand=YES, fill=X)

        path_button = ttk.Button(
            master=path_frame,
            text="选择文件",
            command=self.onBrowse,
            width=8
        )
        path_button.pack(side=LEFT, padx=5)

        self.progressbar = ttk.Progressbar(self, orient=ttk.HORIZONTAL, length=500, mode='determinate')
        self.progressbar['value'] = 0
        self.progressbar.pack(fill=X, padx=10, pady=10)

    def create_results_view(self):
        """Add result treeview to labelframe"""
        self.resultview = ttk.Treeview(
            master=self,
            bootstyle=INFO,
            columns=[0, 1, 2, 3],
            show=HEADINGS
        )
        self.resultview.pack(fill=BOTH, expand=YES, pady=10, padx=10)

        # setup columns and use `scale_size` to adjust for resolution
        self.resultview.heading(0, text='名称', anchor=W)
        self.resultview.heading(1, text='最后修改时间', anchor=W)
        self.resultview.heading(2, text='大小', anchor=E)
        self.resultview.heading(3, text='路径', anchor=W)
        self.resultview.column(
            column=0,
            anchor=W,
            width=utility.scale_size(self, 125),
            stretch=False
        )
        self.resultview.column(
            column=1,
            anchor=W,
            width=utility.scale_size(self, 140),
            stretch=False
        )
        self.resultview.column(
            column=2,
            anchor=E,
            width=utility.scale_size(self, 60),
            stretch=False
        )
        self.resultview.column(
            column=3,
            anchor=W,
            width=utility.scale_size(self, 300)
        )
        self.resultview.bind('<Button-3>', self.showPopup)
        self.popup_menu = ttk.Menu(self.master, tearoff=0)
        self.popup_menu.add_command(label='删除', command=self.deleteSelected)

    def showPopup(self, event):
        item = self.resultview.identify_row(event.y)
        if item:
            self.resultview.selection_set(item)
            self.popup_menu.post(event.x_root, event.y_root)

    def deleteSelected(self):
        selection = self.resultview.selection()
        for item in selection:
            self.resultview.delete(item)

    def createImportButton(self):
        frame = ttk.Frame(self)
        frame.pack(fill=X, expand=YES, padx=10, pady=10)

        backup_button = ttk.Button(
            master=frame,
            text="导入",
            command=self.onImport,
            bootstyle=SUCCESS,
            width=6,
        )

        backup_button.pack(side=RIGHT)

    # 选择文件按钮
    def onBrowse(self):
        # 通过os.path.normpath函数将路径字符串规范化和转义，通过r''取消转义
        file_path = os.path.normpath(r'%s' % self.path_url.get())
        # 通过判断file_path是不是文件，如果是文件判断是不是tar, gz结尾，如果是，说明文件是一个备份文件
        if os.path.isfile(file_path) and file_path.split('.')[1] in ['tar', 'gz']:
            self.addFileInfoToTreeview(file_path)
        else:
            # 通过askopenfilename打开文件选择，通过选择文件的形式，将文件信息导入表格中
            path = askopenfilename(title='打开tar/gz文件', filetypes=[('tar', '*.tar'), ('gz', '*.gz')])
            self.addFileInfoToTreeview(path)

    # 将文件信息添加到表格中
    def addFileInfoToTreeview(self, path):
        # 判断路径是否为空和在导入的列表中是否含有path
        if path and not path in self.import_path_list:
            # 将path加入导入列表中
            self.import_path_list.add(path)
            # 将输入框设置成空
            self.path_url.set("")
            # 获取到文件信息
            file_info = self.getFileInfo(path)
            # 将文件信息导入表格
            self.resultview.insert('', END, values=[file_info['name'], file_info["modified"], file_info['size'], path])

    # 格式化大小
    def getConvertSize(self, size):
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        bt = 1024
        for i in range(len(units)):
            if (size / bt) < 1:
                return "%.2f%s" % (size, units[i])
            size = size / bt

    # 获取选择的文件路径
    def getFileInfo(self, file_path):
        # 获取文件大小（以字节为单位）
        file_size = os.path.getsize(file_path)
        file_size = self.getConvertSize(file_size)
        # 获取最后修改时间
        mod_time = os.path.getmtime(file_path)
        # 格式化修改时间
        mod_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mod_time))
        # 获取文件名
        file_name = os.path.basename(file_path)
        # 打印文件信息
        return {"name": file_name, "size": file_size, "modified": mod_time_str}

    def getAllFiles(self):
        lists = []
        for item in self.resultview.get_children():
            values = self.resultview.item(item, 'values')
            lists.append((values[0], values[3]))
        return lists

    def onImport(self):
        if not self.resultview.get_children():
            messagebox.showwarning(title="导入失败", message="请选择文件")
        else:
            import_tuple = self.getAllFiles()
            print(import_tuple)

            self.import_thread = threading.Thread(target=self.commintThread, args=(import_tuple,), daemon=True)
            self.import_thread.start()

    def commintThread(self, import_paths):
        total = len(import_paths)
        i = 0
        for tu in import_paths:
            if mdm.importImage(tu):
                self.progressbar['value'] = (i + 1) / total * 100
                self.progressbar.update()
                i += 1

        if i == total:
            messagebox.showinfo(title="导入成功", message="导入成功")
        # total = len(backup_tuple)
        # for i, bt in enumerate(backup_tuple):
        #     # print(bt)
        #     # 更新进度条
        #     mdm.backupDocker(bt, path)
        #     self.progressbar['value'] = (i + 1) / total * 100
        #     self.progressbar.update()
        # else:
        #     messagebox.showinfo(title="备份成功", message="备份成功")


class ImportDockerFile:
    def __init__(self):
        self.submit()

    def submit(self):
        path = askopenfilename(title='打开DockerFile文件')

        imagename = simpledialog.askstring(title="输入镜像名", prompt="输入镜像名")
        if imagename is None or imagename == '':
            messagebox.showwarning(title="错误", message="请输入镜像名")
            return

        print(imagename)
        print(path)

        t = threading.Thread(target=self.import_dockerfile, args=(path, imagename))
        t.start()

    def import_dockerfile(self, path, imagename):
        if mdm.importDockerFile(path, imagename):
            messagebox.showinfo(title="导入成功", message="导入成功")
        else:
            messagebox.showwarning(title="导入失败", message="导入失败")
