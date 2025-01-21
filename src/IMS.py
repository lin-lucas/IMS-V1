#!python3

__version__ = '1.8.1'
TIPS_INFO = f'''Item Management System(IMS) V{__version__}
Made by zhilin.tang@qq.com

仓储物品管理系统(物品管家) V{__version__}
作者：zhilin.tang@qq.com'''

from pathlib import Path
import json
import os
import bcrypt
from datetime import datetime
from time import time

rootPath = Path(__file__).parent
things = {}

def initLog():
    global START
    START = time()
    with open(rootPath / 'logs.log', 'w', encoding='utf-8') as file:
        file.write(f'程序在 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 启动。\n')

def log(log:str):
    current = time()
    elapsed = int((current - START) * 1000)
    with open(rootPath / 'logs.log', 'a', encoding='utf-8') as file:
        file.write(f"[{elapsed} ms] {log}\n")

def readInfo():
    global FILE, things, user
    with open(rootPath / f'users.json') as file:
        FILE = json.load(file)
        things = FILE[user]["things"]

def add(index, value):
    log(f'用户添加某物。')
    global FILE, things, user
    try:
        things[index][value] += 1
    except KeyError:
        try:
            things[index]|={value:1}
        except KeyError:
            things[index] = {value:1}
    FILE[user]["things"] = things
    with open(rootPath / f'users.json', 'w') as file:
        print(f'{value} 被添加到 {index}。')
    log('添加成功。')

def delete(index, value):
    log(f'用户删除某物。')
    global things, user
    if index not in things.keys():
        print(f'索引 "{index}" 不存在。')
        return
    try:
        things[index][value] -= 1
        if things[index][value] == 0:
            del things[index][value]
        if len(things[index]) == 0:
            del things[index]
    except KeyError:
        print(f'{value} 不在 {index} 中。')
        return
    FILE[user]["things"] = things
    with open(rootPath / f'users.json', 'w') as file:
        json.dump(FILE, file, indent=4, sort_keys=True)
    print(f'{value} 被从 {index} 中删除。')
    log('删除成功。')

def search(value):
    log(f'用户查询某物。')
    global things
    found = {} # {address: count, ...}
    returnStr = ''
    for i in things.keys():
        for j in things[i].keys():
            if value.lower() in j.lower():
                found[i] = things[i][j]
                returnStr += f'{i}: {things[i][j]}*{j}\n'
    if returnStr == '':
        log('无结果。')
        print('无结果。')
        return 0,''
    else:
        print(f'查询成功：')
        print(returnStr[:-1])
        log('查询成功。')
    return len(found), returnStr

def query(index):
    log(f'用户查询某索引。')
    global things
    if index in things.keys():
        log('查询成功。')
        print('-'*20)
        for value in things[index].keys():
            print(f'{value}*{things[index][value]}')
        print('-'*20)
    else:
        print(f'索引 "{index}" 不存在。')
        log('无结果。')

def display():
    global things
    if len(things) == 0:
        print('无物品。')
        return
    else:
        print('------------')
        for index in things.keys():
            print(index)
            for value in things[index].keys():
                print(f'    {value}*{things[index][value]}')
            print('------------')
        print(f'共 {sum(sum(things[i].values()) for i in things.keys())} 个物品在 {len(things)} 个索引中。')

def login(usr:str, psw:str, num:int=3):
    log(f'用户 {usr} 想要登录。')
    with open(rootPath / 'users.json') as file:
        users:dict = json.loads(file.read())
    if usr in users.keys():
        if psw == users[usr]["password"]:
            log(f'用户 {usr} 登录成功。')
            global user
            user = usr
            print('登录成功。')
            print('欢迎,', user)
            return
        else:
            if num == 0:
                log(f'用户 {usr} 尝试3次，登录失败。')
                print('尝试太多次了！')
                log('程序退出。')
                exit()
            log(f'用户 {usr} 尝试 {num} 次，登录失败。')
            print('用户名或密码错误。')
            usr = input('用户名：')
            psw = input('密码：')
            login(usr, psw, num-1)      
    else:
        if num == 0:
                log(f'用户 {usr} 尝试3次，登录失败。')
                print('尝试太多次了！')
                log('程序退出。')
                exit()
        print('用户名或密码错误。')
        usr = input('用户名：')
        psw = input('密码：')
        login(usr, psw, num-1) 

def logister():
    global FILE, user
    print('请选择([l]登录 / [r]注册 / [e]退出)：')
    choice = input('>>> ')
    match choice.lower():
        case 'l' | 'login':
            log('开始登录。')
            usr = input('用户名：')
            psw = input('密码：')
            user = usr
            login(usr, psw)
            return
        case 'r' |'register':
            log('开始注册。')
            usr = input('用户名：')
            with open(rootPath / 'users.json') as file:
                FILE = json.load(file)
            if usr.lower() in (i.lower() for i in FILE.keys()):
                print('用户名已存在。')
                logister()
            else:
                psw = input('密码：')
                confirm_psw = input('确认密码：')
                if psw!= confirm_psw:
                    print('两次密码不匹配。')
                    log('注册失败。')
                    logister()
                else:
                    FILE[usr] = {"password": psw, "things": {}}
                    with open(rootPath / f'users.json', 'w') as file:
                        json.dump(FILE, file, indent=4, sort_keys=True)
                    print('注册成功。')
                    user = usr
                    login(usr, psw)
                    return
        case 'e' | 'exit':
            log('程序结束。')
            exit()
        case _:
            print('输入不合法。')
            logister()

def main():
    initLog()
    print(TIPS_INFO)
    log('程序启动。')
    try:
        with open(rootPath / 'users.json'):
            pass
    except FileNotFoundError:
        log('用户数据文件不存在，正在创建。')
        with open(rootPath / 'users.json', 'w') as file:
            json.dump({}, file, indent=4, sort_keys=True)
    logister()
    readInfo()
    log('数据文件加载。')
    # Main loop
    keep_going = True
    log('主循环开始。')
    while keep_going:
        command = input('>>> ')
        match command.lower():
            case 'add' | 'a':
                try:
                    index = input('索引：')
                    value = input('物品：')
                    count = int(input('数量：'))
                except:
                    print('输入不合法。')
                    continue
                else:
                    for _ in range(count):
                        add(index, value)

            case 'delete' | 'dl' | 'dlt':
                try:
                    index = input('索引：')
                    value = input('物品：')
                    count = int(input('数量：'))
                except:
                    print('输入不合法。')
                    continue
                else:
                    for _ in range(count):
                        delete(index, value)

            case'search' | 's'| 'sc' | 'find' | 'fd' | 'f':
                try:
                    value = input('物品：')
                except:
                    print('输入不合法。')
                    continue
                else:
                    search(value)

            case 'query' | 'q':
                try:
                    index = input('索引：')
                except:
                    print('输入不合法。')
                    continue
                else:
                    query(index)
            
            case 'clear' | 'cls':
                os.system('cls')

            case 'display' | 'd' | 'dis':
                display()

            case 'help' | 'h':
                print(f'''{TIPS_INFO}
==================== 命 令 指 南 =======================
                    add, a - 添加某物品到某索引。
           delete, dl, dlt - 从某索引删除某物品。
search, s, sc, find, fd, f - 查询某物品。
                  query, q - 查询某索引。
                clear, cls - 清屏。
           display, d, dis - 显示所有物品。
                   help, h - 显示这条帮助信息。
                exit, quit - 退出程序。
========================================================''')

            case 'exit' | 'quit':
                log('程序结束。')
                keep_going = False

            case _:
                print('输入不合法。')
                continue

if __name__ == '__main__':
    main()