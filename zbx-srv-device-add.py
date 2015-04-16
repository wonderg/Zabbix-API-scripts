#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = 'gostepan'

import sys
import argparse
from pyzabbix import ZabbixAPI

zaurl = "http://zabbix.net/"
zalogin = "admin"
zapassword = "password"

def createParser ():
    parser = argparse.ArgumentParser(
        prog='zabbix_host_add',
        description='''Скрипт добавления устройст в заббикс с заданным именем, ip-адресом, группой, шаблоном, типом устройства и mac-адресом''',
        )

    parser.add_argument('-ho', '--host', help='имя хоста')
    parser.add_argument('-n', '--name', help='видимое имя хоста, можно кириллицей')
    parser.add_argument('-i', '--ipadd', help='ip-адрес хоста')
    parser.add_argument('-g', '--group', help='номер группы, куда необходимо добавить хост')
    parser.add_argument('-t', '--template', help='номер шаблона, который необходимо прикрепить к хосту')
    parser.add_argument('-d', '--dev_type', help='тип устройства для инвентарных данных')
    parser.add_argument('-m', '--macadd', default='00:00:00:00:00:00', help='mac-адрес для инвентарных данных')
    return parser


def create_host(host, name, ip, group, template, dev_type, macadd):
    group = group.decode('utf-8')
    zapi = ZabbixAPI(zaurl)

    # Enable HTTP auth
    zapi.session.auth = (zalogin, zapassword)

    # Disable SSL certificate verification
    zapi.session.verify = False

    # Specify a timeout (in seconds)
    zapi.timeout = 5.1

    # Login (in case of HTTP Auth, only the username is needed, the password, if passed, will $
    zapi.login(zalogin, zapassword)


    zapi.host.create({"host":host, "name":name,
                    "interfaces":[{
                                    "type":2, "dns":"",
                                    "main":1,
                                    "ip":ip,
                                    "port":161,
                                    "useip":1}],
                    "groups":    [{"groupid": group}],
                    "templates": [{ "templateid":template }],
                    "inventory": {"type":dev_type,"macaddress_a":macadd }
                    })

    for h in zapi.host.get(output="extend", search={"host": host}):
    #     print h
        string = h['name']+" "+h['host']+" "+h['hostid']
        string = string.encode('ascii', 'ignore')
        print(string)

if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    create_host(namespace.host, namespace.name, namespace.ipadd, namespace.group, namespace.template, namespace.dev_type, namespace.macadd)
