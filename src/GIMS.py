from tkinter import *
from __init__ import *

def _add(win:Tk,directory, name):
    add(directory, name)
    win.destroy()

def _login(win:Tk,username, password):
    login(username, password)
    win.destroy()

def GUI_login():
    window = Tk()
    window.title("登录")
    window.geometry("200x120")
    Label(window, text="用户名：").pack()
    username = Entry(window)
    username.pack()
    Label(window, text="密码：").pack()
    password = Entry(window, show="*")
    password.pack()
    Button(window, text="登录", width=10, command=lambda: _login(window,username.get(), password.get())).pack()
    window.mainloop()

def GUI_add():
    window = Tk()
    window.title("添加")
    window.geometry("200x120")
    Label(window, text="目录：").pack()
    directory = Entry(window)
    directory.pack()
    Label(window, text="名称：").pack()
    name = Entry(window)
    name.pack()
    Button(window, text="确定", width=10, command=lambda: _add(window,directory.get(), name.get())).pack()
    window.mainloop()

def main():
    GUI_login()
    readInfo()
    root = Tk()
    root.title("仓储物品管理系统")
    root.geometry("1000x600")

    # Menu
    menu = Menu(root)
    menu.add_command(label='添加', command=GUI_add)
    root.config(menu=menu)
    # Display
    Label(root, text="仓库").pack()
    Text(root, height=20, width=50).pack()
    root.mainloop()

if __name__ == '__main__':
    main()