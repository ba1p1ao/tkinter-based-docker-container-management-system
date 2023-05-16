import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import winpty
import threading

class TerminalFrame(ttk.Frame):
    def __init__(self, master, ):
        super().__init__(master, padding=(10, 20))
        self.master = master
        self.pack(fill=BOTH, expand=YES)
        self.is_run_thread = True
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
        self.term.spawn('ssh root@192.168.10.101')
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
            self.output.configure(state=NORMAL)
            self.output.insert(END, data)
            self.output.configure(state=DISABLED)
            self.output.see(END)

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
    def __del__(self):

        print('123')

root = ttk.Window("Terminal", "superhero")
TerminalFrame(root)
root.mainloop()
