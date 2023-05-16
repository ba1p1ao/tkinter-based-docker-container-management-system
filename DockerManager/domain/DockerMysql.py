#!/usr/bin/env python3
# @Time : 2023/04/13 0013 23:10
# @Author : cui shi yuan
# @File : DockerMysql.py

import MySqlClass
import MyDockerManager

msc = MySqlClass.MySqlClass('192.168.10.101', 'root', '123', 'testdb')
mdm = MyDockerManager.MyDockerManager("192.168.10.101", "2375")


# 添加容器
def insertDocker(container):
    msc.insertData("insert into containers values(%s, %s, %s, %s, %s, %s)",
                   container['id'], container['name'], container['image'], container['created'],
                   container['status'], container['ports'])


# 删除容器
def deleteDocker(container):
    msc.deleteData("delete from containers where container_id=%s", container['id'])


# 修改容器
def updateDocker(container):
    msc.updateData(
        "update containers set container_name = %s, image = %s, created = %s, status = %s, ports = %s where container_id = %s",
        container['name'], container['image'], container['created'],
        container['status'], container['ports'], container['id'])


# 添加镜像
def insertImage(image):
    msc.insertData("insert into images values(%s, %s, %s, %s, %s)",
                   image['id'], image['name'], image['tag'], image['created'], image['size'])


# 删除镜像
def deleteImage(image):
    msc.deleteData("delete from images where image_id = %s", image['id'])


'''

containers 数据库，属性对应关系
    container['id'] = container_id
    container['name'] = container_name
    container['image'] = image
    created = container['created']
    status = container['statud']
    ports = container['ports']
    
images 数据库属性对应关系
    image_id = images['id'] 
    image_name = images['name'] 
    image_version = images['tag'] 
    created = image['created'] 
    size = image['size']
'''


# 同步所有的容器
def syncDocker():
    msc.deleteData("delete from containers")
    containers = mdm.getAllDockers()
    for container in containers:
        if msc.query("select * from containers where container_id = %s", container['id']):
            updateDocker(container)
        else:
            insertDocker(container)


# 同步所有的镜像
def syncImage():
    msc.deleteData("delete from images")
    images = mdm.getAllImages()
    mdm.showImages()
    for image in images:
        if not msc.query("select * from images where image_id = %s and image_name = %s and image_version = %s",
                         image['id'], image['name'], image['tag']):
            insertImage(image)


if __name__ == '__main__':
    syncDocker()
    syncImage()
