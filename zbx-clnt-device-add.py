#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'gostepan'

import sys
import os
import paramiko
import re


zaurl = '192.168.0.1'
zauser = 'user'
zapass = 'password'

#FORM = ['host', 'name', 'ip', 'group', 'template', 'dev_type', 'macadd']
#DATA = []
PATH = 'list.txt'

link2script = '/home/zbx-srv-device-add.py' # lint to server scipt

#  Main definition - constants
menu_actions = {}

# =======================
#     MENUS FUNCTIONS
# =======================

# Main menu

def main_menu():
    os.system('CLS')
    print('Добавить устройство в Zabbix вручную или по списку?')
    print("1. Вручную")
    print("2. По списку")
    print("\n0. Выход")
    choice = input(" >>  ")
    exec_menu(choice)

    return


# Execute menu
def exec_menu(choice):
    os.system('CLS')
    ch = choice.lower()
    if ch == '':
        menu_actions['main_menu']()
    else:
        try:
            menu_actions[ch]()
        except KeyError:
            print("Некорректный ввод\n")
            menu_actions['main_menu']()
    return


# Menu 1
def manual_device_add():
    print("[Ручное добавление устройства]\n")
    host = input("[Введите название хоста латиницей]\n")
    name = input("[Введите видимое имя хоста на русском]\n")
    ip = input("[Введите IP]\n")
    group = input("[Введит ID-группы в которую добавляем хост. VoIP - 53, ATS - 52, IAD - 62 либо любой другой ID]\n")
    if group == '52':
        dev_type = "ATS"
    elif group == '53':
        dev_type = "SIPGateway"
    elif group == '62':
        dev_type = "IAD"
    else:
        dev_type = input("[Введите тип устройства]\n 1. PBX\n 2. SIPGateway\n 3. IAD\n")
        if dev_type == '1':
            dev_type = "PBX"
        elif dev_type == '2':
            dev_type = "SIPGateway"
        elif dev_type == '3':
            dev_type = "IAD"
    template = input("[Какой шаблон прикрепить? Если стандартный шаблон ATS ICMP Ping, то нажмите ENTER]\n")
    if template == '':
        template = "10115"
    macadd = input("[Введите MAC-адрес устройства, если неизвестен, то нажмите ENTER]\n")
    if macadd == '':
        macadd = "00:00:00:00:00:00"
    FORM = ['host', 'name', 'ip', 'group', 'template', 'dev_type', 'macadd']
    DATA = [host, name, ip, group, template, dev_type, macadd]
    DICT = dict(zip(FORM, DATA))
    print("\r\n[ПРОВЕРЬТЕ ВВЕДЁННЫЕ ДАННЫЕ]\n")
    print('Имя узла: ' + DICT['host'] + '\n')
    print('Видимое имя узла: ' + DICT['name'] + '\n')
    print('IP-адрес: ' + DICT['ip'] + '\n')
    print('Номер группы: ' + DICT['group'] + '\n')
    print('Номер шаблона: ' + DICT['template'] + '\n')
    print('Тип девайса: ' + DICT['dev_type'] + '\n')
    print('MAC-адрес: ' + DICT['macadd'] + '\n')
    print('\n')
    print("Всё корректно?\n 1. Да\n 2. Нет\n 3. Вернуться в предыдущее меню\n")
    check = input(" >>  ")
    if check == "1":
        cmd = 'python ' + link2script + ' ' + ' --host \"' + DICT['host'] + '\" --name \"' + DICT['name'] + \
             '\" --ipadd \"' + DICT['ip'] + '\" --group \"' + DICT['group'] + '\" --template \"' + DICT['template'] +\
             '\" --dev_type \"' + DICT['dev_type'] + '\" --macadd \"' + DICT['macadd'] + '\"'
        print('\n' + 'Отправка запроса на Zabbix-сервер\n' )
        print(cmd)
        runSshCmd(zaurl, zauser, zapass, cmd)
        print("\n Устройство добавлено \n")
        print("1. Добавить ещё одно устройство")
        print("9. Назад")
        print("0. Выход")
        choice = input(" >>  ")
        exec_menu(choice)
    elif check == '3':
        exec_menu('main_menu')
    else:
        exec_menu('1')
    return DICT

#DICT = {'template': '10115', 'name': 'Марату 47 Я покупаю СПБ1 RG-2402G', 'host': 'Marata 47 Ja pokupaju SPB1 RG-2402G',
#        'ip': '192.168.12.38', 'group': '53', 'dev_type': 'SIPGateway', 'macadd': '5C:50:15:42:E6:40'}

# Menu 2
def list_device_add():
    print("[Добавление устройств по списку]\n")

    with open(PATH, 'r') as f:
        for line in f:
            print(line)
            DATA = []
            FORM = ['host', 'name', 'ip', 'group', 'template', 'dev_type', 'macadd']
            for i in re.split('%', line):
                DATA.append(i)
            DICT = dict(zip(FORM, DATA))
            print("Device " + DICT["host"] + " " + DICT["ip"] + " is added\n")
            cmd = 'python ' + link2script + ' ' + ' --host \"' + DICT['host'] + '\" --name \"' + DICT['name'] + \
            '\" --ipadd \"' + DICT['ip'] + '\" --group \"' + DICT['group'] + '\" --template \"' + DICT['template'] +\
            '\" --dev_type \"' + DICT['dev_type'] + '\" --macadd \"' + DICT['macadd'] + '\"'
            runSshCmd(zaurl, zauser, zapass, cmd)

    print("9. Назад")
    print("0. Выход")
    choice = input(" >>  ")
    exec_menu(choice)
    return


# Back to main menu
def back():
    menu_actions['main_menu']()


# Exit program
def exit():
    sys.exit()

# =======================
#    MENUS DEFINITIONS
# =======================

# Menu definition
menu_actions = {
    'main_menu': main_menu,
    '1': manual_device_add,
    '2': list_device_add,
    '9': back,
    '0': exit,
}

# =======================
#      MAIN PROGRAM
# =======================


def runSshCmd(hostname, username, password, cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
#    ssh.connect('10.17.100.73',username='mak',password='Secret2012!')
    stdin,stdout,stderr = ssh.exec_command(cmd)
    #print(stdout.read().decode("utf-8"))
    ssh.close()


# Main Program
if __name__ == "__main__":
    # Launch main menu
    main_menu()
