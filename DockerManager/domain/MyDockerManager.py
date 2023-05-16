#!/usr/bin/env python3
# @Time : 2023/04/01 0001 15:01
# @Author : cui shi yuan
# @File : MyDockerManager.py

import docker
import os
import traceback
import subprocess
import re

from domain import MySqlClass
from utils import ConnectShell


class MyDockerManager:

    def __init__(self, ip, port):
        self.client = docker.DockerClient(base_url="tcp://%s:%s" % (ip, port))
        self.connectShell = ConnectShell.ConnectShell(ip, "root", "123", "22")

    @staticmethod
    def handleException(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(e, "参数输入有误")
                print(traceback.format_exc())

        return wrapper

    @staticmethod
    def getCreatedDateTime(dateString):
        l = re.split(r'[A-Za-z|.]', dateString)
        return l[0] + " " + l[1]

    @staticmethod
    def getConvertSize(text):
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = 1024
        for i in range(len(units)):
            if (text / size) < 1:
                return "%.2f%s" % (text, units[i])
            text = text / size

    def getDockerName(self, tags):
        if not tags:
            return []
        elif tags[0].find("/") != -1:
            return re.split(r'/', tags[0])[1]
        else:
            return tags[0]

    # 获取所有的docker容器，并返回列表，其中每一个docker的信息已字典的形式返回
    def getAllDockers(self):
        containers = self.client.containers.list(all=True)
        containerDictList = []

        for container in containers:
            ports = ''
            for k in container.ports.keys():
                ports += k
            containerDictList.append({
                'id': container.short_id,
                # 'image': 'ubuntu',
                'image': self.getDockerName(container.image.tags),
                'name': container.name,
                'status': container.status,
                'ports': ports,
                'created': self.getCreatedDateTime(container.attrs['Created'])
            })

        return containerDictList

    # 获取单个容器，满足符合输入的键值对的容器
    def getOneContainer(self, **kwargs):
        containers = self.getAllDockers()
        for container in containers:
            if all(container[k] == v for k, v in kwargs.items()):
                return container

    # 获取所有的image，并返回列表，其中每一个image的信息已字典的形式返回
    def getAllImages(self):
        images = self.client.images.list(all=True)
        imageDictList = []
        for image in images:
            tags = image.tags if image.tags else ['<none>']
            for tag in tags:
                imageDictList.append({
                    'id': image.short_id.split(':')[1],
                    'name': '<none>' if tag == '<none>' else re.split(r'[/:]', tag)[1],
                    'tag': '<none>' if tag == '<none>' else tag.split(':')[1],
                    'created': self.getCreatedDateTime(image.attrs['Created']),
                    'size': self.getConvertSize(image.attrs['Size'])
                })

        return imageDictList

    def getOneImage(self, **kwargs):
        images = self.getAllImages()
        for image in images:
            if all(image[k] == v for k, v in kwargs.items()):
                return image

    # 判断docker容器是否存在
    def isExistDocker(self, container):
        container_exists = self.getOneContainer(name=container)
        return container_exists

    # 判断images镜像是否存在
    def isExistImage(self, image):
        image_exists = self.getOneImage(id=image)
        return image_exists

    # @handleException
    # 删除docker容器
    def removeDockers(self, **kwargs):
        # 获取所有的docker
        containers = self.getAllDockers()
        try:
            # 用来判断docker容器是否存在
            isFind = False
            for container in containers:
                # 判断输入的键值对在docker容器列表中是否有完全匹配的
                if all(container[k] == v for k, v in kwargs.items()):
                    self.client.containers.get(container['id']).remove(force=True)
                    isFind = True
                    print("%s, %s容器已经被删除" % (container['id'], container['image']))
                    return True
            if not isFind:
                print("没有找到该容器")
        except Exception as e:
            print(e, "参数输入有误")
            print(traceback.format_exc())
            return False

    # @handleException
    # 删除images
    def removeImages(self, **kwargs):
        # 获取所有的images
        images = self.getAllImages()
        try:
            # 用来判断images容器是否存在
            isFind = False
            for image in images:
                # 判断输入的键值对在images列表中是否有完全匹配的
                if all(image[k] == v for k, v in kwargs.items()):
                    self.client.images.get(image['id']).remove()
                    isFind = True
                    print("%s, %s成功被删除" % (image['id'], image['tag']))
                    return True
            if not isFind:
                print("没有找到该镜像")
        except Exception as e:
            print(e, "参数输入有误")
            print(traceback.format_exc())
            return False

    def createDocker(self, **kwargs):
        print(kwargs)
        # 输入参数校验
        try:
            # image 是镜像的id
            image = str(kwargs['image'])
            im = self.client.images.get(image)
            print(im.tags)
            name = str(kwargs['name'])
        except KeyError as e:
            print("缺少必要的输入参数: %s" % str(e))

        # 检查容器是否已存在
        if self.isExistDocker(name):
            print("%s容器已经存在" % name)
            return "isExist"
        # 创建Docker容器
        try:
            container = self.client.containers.run(image=im.tags[0], name=name, detach=True)
            return "success"
            # container = self.getOneContainer(image=image, name=name)
            # image = self.getOneImage(name=image)
            # dm.insertDocker(container, image)
        except docker.errors.ImageNotFound:
            print("Docker镜像不存在: %s" % image)
        except docker.errors.APIError as e:
            print("创建Docker容器失败: %s" % str(e))

    # 拉取镜像
    def pullImage(self, image_name, tag="latest"):
        image = self.client.images.pull(image_name, tag=tag)
        return image

    def pullImageAPI(self, image_name, tag="latest"):
        image = self.client.api.pull(image_name, tag=tag, stream=True)
        return image

    def startDocker(self, container):
        # 启动Docker容器
        self.connectShell.commit("docker start %s" % container)

    def stopDocker(self, container):
        # 停止Docker容器
        self.connectShell.commit("docker stop %s" % container)

    def restartDocker(self, container):
        # 重启Docker容器
        self.connectShell.commit("docker restart %s" % container)

    def logDocker(self, container):
        print("../logs/%s-%s.log" % (container[0], container[1]))
        with open("E:/programming/pythonTest/DockerManager/logs/%s-%s.log" % (container[0], container[1]), "w") as f:
            logs = self.client.containers.get(container[0]).logs().decode('utf-8')
            print(logs)
            f.writelines(logs)

    # 修改容器
    def updateContainer(self, name, newname, status):
        container = self.client.containers.get(name)
        # 更新容器的状态
        container.start() if status == 'running' else container.stop()
        if name != newname:
            container.rename(newname)

    # 备份容器
    def backupDocker(self, container, path):

        self.startDocker(container[0])
        print(container[1])
        self.connectShell.commit('docker export %s > /tmp/container_%s.tar' % (container[0], container[1]))
        self.connectShell.getFile("/tmp/container_%s.tar" % container[1], path + "/container_%s.tar" % container[1])
        self.stopDocker(container[0])
        print("==========success============")

        return True

    # 备份镜像
    def backupImage(self, images, path):
        print(images[1])
        self.connectShell.commit("docker save %s > /tmp/image_%s.tar" % (images[0], images[1]))
        self.connectShell.getFile("/tmp/image_%s.tar" % images[1], path + "/image_%s.tar" % images[1])
        print("==========success============")
        return True

    # 导入镜像
    def importImage(self, images):
        print(images[0])
        self.connectShell.putFile(images[1], "/tmp/my_%s" % images[0])
        self.connectShell.commit("cat /tmp/my_%s | docker import - %s" % (images[0], images[0].split('.')[0]))
        print("==========success============")
        return True

    # 导入dockerfile文件
    def importDockerFile(self, dockerfile, imagename):
        filename = os.path.basename(dockerfile)
        self.connectShell.putFile(dockerfile, "/tmp/%s" % filename)
        self.connectShell.commit("docker build -t %s /tmp" % imagename)
        print("==========success============")
        return True

    # 输出所有的images
    def showImages(self):
        for i in self.getAllImages():
            print(i)

    # 输出所有的dockers
    def showDockers(self):
        for i in self.getAllDockers():
            print(i)

    def showDockersLinux(self):
        print(self.connectShell.commit("docker ps -a"))

    def showImagesLinux(self):
        print(self.connectShell.commit("docker images -a"))

    def isUsedImage(self):
        images = self.client.images.list()
        for image in images:
            for container in self.client.containers.list(all=True):
                if image.tags and image.tags[0] in container.image.tags:
                    print(f"Image {image.tags[0]} is used by container {container.name}")


if __name__ == '__main__':
    mdm = MyDockerManager("192.168.10.101", "2375")
    msc = MySqlClass.MySqlClass("192.168.10.101", "root", '123', 'testdb')
    # print(mdm.getAllDockers())
    # l1 = mdm.getAllImages()
    # for con in l1:
    #     # print(con)
    #     # if con['name'] == '<none>':
    #     mdm.removeImages(name='<none>')
    #         # print(con['id'], con['name'])
    # mdm.removeImages(id='eeb6ee3f44bd')

    # containers = msc.getAll("select * from containers")
    # for con in containers:
    #     print(con)
    #     mdm.createDocker(image=con['image_name'], name=con['container_name'])
    # print(mdm.getOneContainer(name="mynignx1"))
    # for image in images:
    #     # print(image)
    #     print(image['image_name'], image['image_version'])
    # mdm.pullImage(image['image_name'], image['image_version'])
    # mdm.showDockers()
    # mdm.startDocker("1f05521464c1")
    # dm.syncDocker(mdm.getAllDockers(), mdm.getAllImages())
    # mdm.startDocker('mynignx1')
    # mdm.removeDockers(mage='nginx')
    # mdm.showDockers()
    # mdm.createDocker(image='nginx', name='my-nginx3')
    # mdm.getOneContainer(image='nginx', name='my-nginx3')
    # mdm.startDocker('mynginx1')
    # mdm.removeDockers(image='nginx', name='my-nginx3')
    # mdm.createImage('nginx')
    # mdm.pullImage("nginx")
    # mdm.removeImages(name='nginx')
    # print(mdm.removeImages(id="5a214d77f5d7"))
    mdm.showDockers()
    mdm.showImages()
    mdm.isUsedImage()
    # mdm.showImages()
    # mdm.updateContainer('my-nginx2')
    # mdm.createImage('')
    # mdm.removeImages(id="5d0da3dc9764")
    # mdm.removeDockers(image='nginx')
    # mdm.showImages()
    # mdm.showImagesLinux()
    # mdm.showDockersLinux()
    # mdm.logDocker("my-nginx2")
    # mdm.showDockersLinux()

    # mdm.pullImage("ubuntu")
    # mdm.showImages()
    # print(mdc.isExistDocker("mynignx1"))
