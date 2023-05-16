#!/usr/bin/env python3
# @Time : 2023/04/20 0020 10:16
# @Author : cui shi yuan
# @File : ConnectShell.py
import time

import paramiko
import os
import FunctionClass as fc


class ConnectShell:
    def __init__(self, ip, username, password, port):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            # 连接远程虚拟机
            if fc.isOnline(ip, port):
                self.ssh.connect(ip, port, username, password, timeout=5)
        except Exception as e:
            print("Authentication failed")
            return

    def commit(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        result = stdout.read().decode('utf-8')
        return result

    def putFile(self, localPath, linuxPath):
        sftp = self.ssh.open_sftp()
        remoteDir = os.path.dirname(linuxPath)
        try:
            sftp.stat(remoteDir)
        except Exception as e:
            sftp.mkdir(remoteDir)
        with open(localPath, 'rb') as f:
            sftp.putfo(f, linuxPath)
        sftp.close()

    def getFile(self, linuxPath, localPath):
        sftp = self.ssh.open_sftp()
        with open(localPath, 'wb') as f:
            sftp.getfo(linuxPath, f)
        sftp.close()

    def __del__(self):
        self.ssh.close()


if __name__ == '__main__':
    cs = ConnectShell("192.168.10.101", "root", "123", "22")
    a = time.time()
    cs.getFile("/root/abc", "E:/Desktop/test/abc")
    b = time.time()
    print(b - a)
    # print()
    # print(cs.commit("docker logs f6efde226a0e"))
