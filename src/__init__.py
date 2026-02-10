from time import time
from datetime import datetime
import os
import json
from pathlib import Path

__version__ = '1.10.0-test-20260205'
TIPS_INFO = f"""Item Management System(IMS) V{__version__}
Made by zhilin.tang@qq.com

仓储物品管理系统(物品管家) V{__version__}
作者：zhilin.tang@qq.com"""


rootPath: Path = Path(__file__).parent
things: dict[str, dict[str, int]] = {}
FILE: dict[str, dict] = {}
LANG: dict[str, str]
login_num:int=3


class UserError(Exception):
    pass
class BarcodeError(Exception):
    pass


def initLog() -> None:
    global START
    START = time()
    with open(rootPath / 'logs.log', 'w', encoding='utf-8') as file:
        file.write(f'程序在 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 启动。\n')


def log(msg: str) -> None:
    current = time()
    elapsed = int((current - START) * 1000)
    with open(rootPath / 'logs.log', 'a', encoding='utf-8') as file:
        file.write(f'[{elapsed} ms] {msg}\n')


def language() -> None:
    global LANG
    user_language = input(
        'Choose language / 选择语言\n[E]nglish / [C]简体中文\n>>> '
    ).lower()
    if user_language == 'e':
        with open(rootPath / 'lang' / 'en_us.json', encoding='utf-8') as file:
            LANG = json.load(file)
    elif user_language == 'c':
        with open(rootPath / 'lang' / 'zh_cn.json', encoding='utf-8') as file:
            LANG = json.load(file)


def readInfo() -> None:
    global FILE, things, user
    things = FILE[user]['things']


def saveFile() -> None:
    with open(rootPath / 'users.json', 'w', encoding='utf-8') as file:
        json.dump(FILE, file, indent=4, sort_keys=True)


def hashPassword(psw: str) -> int:
    s = 0
    for j, i in enumerate(psw):
        n = ord(i)
        s += n*(37**j)
        s %= (1e8+7)
    return int(s)

def _checkBarcode(code:str)->bool:
    if(len(code)!=8):
        return False
    try:
        a = 3*(
            int(code[0])+
            int(code[2])+
            int(code[4])+
            int(code[6])
        )
        b = (
            int(code[1])+
            int(code[3])+
            int(code[5])+
            int(code[7])
        )
    except:
        return False
    if (a + b) % 10 == 0:
        return True
    else:
        return False

def getLocation(index:str)->str:
    if not _checkBarcode(index):
        raise BarcodeError
    place = index[0:3]
    level = index[3:5]
    order = index[5:]
    returnStr = f'{FILE[user]['places'][place]} {int(level)} 层 第 {int(order)} 个容器'
    return returnStr

def add(index: str, value: str, count: int = 1) -> None:
    log(f'用户添加某物。')
    if count <= 0:
        print(LANG['add.illegal_count'])
        return
    global things
    try:
        things[index][value] += count
    except KeyError:
        try:
            things[index][value] = count
        except KeyError:
            things[index] = {value: count}
    saveFile()
    log('添加成功。')


def delete(index: str, value: str, count: int = 1) -> None:
    log(f'用户删除某物。')
    if count <= 0:
        print(LANG['delete.illegal_count'])
        return
    global things, user
    if index not in things.keys():
        print(LANG['delete.index_does_not_exist'].format(index))
        return
    try:
        if count <= things[index][value]:
            things[index][value] -= count
            if things[index][value] == 0:
                del things[index][value]
            if things[index] == {}:
                del things[index]
        else:
            print(LANG['delete.not_enough_items'])
            return
    except KeyError:
        print(LANG['delete.item_does_not_exist'].format(value, index))
        return
    else:
        print(LANG['delete.delete_successfully'].format(value, index))
        saveFile()
        log('删除成功。')


def search(value: str):
    log('用户查询某物。')
    global things
    found = {}
    returnStr = ''
    for i in things.keys():
        for j in things[i].keys():
            if value.lower() in j.lower():
                found[i] = things[i][j]
                try:
                    returnStr += f'{i} [{getLocation(i):17}]: {things[i][j]}*{j}\n'
                except BarcodeError:
                    returnStr += f'{i} [{LANG['getLocation.unknown_place']}]: {things[i][j]}*{j}\n'
    if returnStr == '':
        log('无结果。')
        print(LANG['search.no_result'])
    else:
        print(f'查询成功：')
        print(returnStr[:-1])  # 去掉换行
        log(LANG['search.successfully'])


def query(index: str) -> None:
    log(f'用户查询某索引。')
    global things
    if index in things.keys():
        log('查询成功。')
        print('-' * 20)
        for value in things[index].keys():
            print(f'{value}*{things[index][value]}')
        print('-' * 20)
    else:
        print(LANG['query.index_does_not_exist'].format(index))
        log('无结果。')


def display() -> None:
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
        print(
            LANG['display.msg'].format(
                sum(sum(things[i].values()) for i in things.keys()), len(things))
        )


def login(usr: str, psw: str):
    global login_num
    if usr not in FILE.keys():
        print(LANG['login.usr_does_not_exist'])
        raise UserError('User does not exist.')
    if hashPassword(psw) == FILE[usr]['password']:
        print(LANG['login.welcome'].format(usr))
        print(LANG['main.help'])
        return
    else:
        login_num-=1
        print(LANG['login.wrong_password'])
        print(LANG['login.failed'].format(login_num))
        if login_num==0:
            exit()
        logister()


def logister():
    global FILE, user
    print('请选择([l]登录 / [r]注册 / [e]退出)：')
    choice = input('>>> ')
    match choice.lower():
        case 'l' | 'login':
            log('开始登录。')
            usr = input(LANG['logister.username'])
            psw = input(LANG['logister.password'])
            user = usr
            try:
                login(usr, psw)
            except UserError:
                logister()
            return
        case 'r' | 'register':
            log('开始注册。')
            usr = input(LANG['logister.username'])
            with open(rootPath / 'users.json') as file:
                FILE = json.load(file)
            if usr.lower() in (i.lower() for i in FILE.keys()):
                print(LANG['logister.user_has_exist'])
                logister()
            else:
                psw = input(LANG['logister.password'])
                confirm_psw = input(LANG['logister.confirm_password'])
                if psw != confirm_psw:
                    print(LANG['logister.password_not_match'])
                    log('注册失败。')
                    logister()
                else:
                    FILE[usr] = {'password': hashPassword(psw), 'things': {}}
                    saveFile()
                    print(LANG['logister.welcome'])
                    user = usr
                    login(usr, psw)
                    return
        case 'e' | 'exit':
            log('程序结束。')
            exit()
        case _:
            print(LANG['main.illegal_input'])
            logister()


def main():
    global FILE
    initLog()
    print(TIPS_INFO)
    log('程序启动。')
    language()
    try:
        with open(rootPath / 'users.json'):
            pass
    except FileNotFoundError:
        log('用户数据文件不存在，正在创建。')
        with open(rootPath / 'users.json', 'w') as file:
            json.dump({}, file, indent=4, sort_keys=True)
    with open(rootPath / 'users.json', encoding='utf-8') as file:
        try:
            FILE = json.load(file)
        except json.JSONDecodeError:
            FILE = {}
            saveFile()
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
                    index = input(LANG['main.index'])
                    value = input(LANG['main.value'])
                    count = int(input(LANG['main.count']))
                except:
                    print(LANG['main.illegal_input'])
                    continue
                add(index, value, count)

            case 'delete' | 'dl' | 'dlt':
                try:
                    index = input(LANG['main.index'])
                    value = input(LANG['main.value'])
                    count = int(input(LANG['main.count']))
                except:
                    print(LANG['main.illegal_input'])
                    continue

                delete(index, value, count)

            case 'search' | 's' | 'sc' | 'find' | 'fd' | 'f':
                try:
                    value = input(LANG['main.value'])
                except:
                    print(LANG['main.illegal_input'])
                    continue
                else:
                    search(value)

            case 'query' | 'q':
                try:
                    index = input(LANG['main.index'])
                except:
                    print(LANG['main.illegal_input'])
                    continue
                else:
                    query(index)

            case 'clear' | 'cls':
                os.system('cls')

            case 'display' | 'd' | 'dis':
                display()

            case 'l' | 'lang':
                language()

            case 'help' | 'h':
                print(f'{TIPS_INFO}\n{LANG['main.help']}')

            case 'exit' | 'quit':
                log('程序结束。')
                keep_going = False

            case _:
                print(LANG['main.illegal_input'])
                continue


if __name__ == '__main__':
    main()
