import tkinter.messagebox
from tkinter import *
from tkinter import ttk
from tkcalendar import Calendar, DateEntry
import os.path
import configparser
from functions import get_users_from_department, make_df_from_xlsx
from myfunctions import distr_json
import re
import cryptocode
import win32security
import subprocess
from orm import get_users

settings = configparser.ConfigParser()
settings.read('settings.ini')

current_machine_id = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
desc = win32security.GetFileSecurity(".", win32security.OWNER_SECURITY_INFORMATION)
sid = desc.GetSecurityDescriptorOwner()
sidstr = win32security.ConvertSidToStringSid(sid)
key = current_machine_id[-12:] + sidstr[-15:-5] + current_machine_id[:8] + sidstr[-4:]

width = 580
height = 380
if settings['db']['db_users'] == 'yes':
    df = get_users(login=True, name=True)
else:
    df = make_df_from_xlsx('users.xlsx')
login = ''
password = ''
n = ''
t = ''
user_login = ''
role = ''
role_ = ''
dep = ''
date = ''
date_ = ''
reg_sub = ''


def center(win, w, h):
    """
    centers a tkinter window
    :param w: width win
    :param h: height win
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    # width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = w + 2 * frm_width
    # height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = h + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(w, h, x, y))
    win.deiconify()


def normal(word=''):
    layout = dict(zip(map(ord, "йцукенгшщзхъфывапролджэячсмитьбю.ё"
                               'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё'),
                      "qwertyuiop[]asdfghjkl;'zxcvbnm,./`"
                      'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~'))
    log = login.translate(layout).lower()
    pas = password.translate(layout)
    if word == 'login':
        return log
    if word == 'password':
        return pas
    return log, pas


exit_flag = False


def return_id():
    form()
    if exit_flag:
        return False
    if settings['db']['db_users'] == 'yes':
        df = get_users(org_id=dep, login=True, name=True)
    return login, password, n, t, user_login, role, dep, date, df, role_, date_, reg_sub


def form():
    def exit_from_form():
        global exit_flag
        exit_flag = True
        root.destroy()

    def check_input(_event=None):
        value = combo_user.get().lower()

        if value == '':
            listbox_values.set(users)
        else:
            data = []
            for item in users:
                if value.lower() in item[1].lower():
                    data.append(item)

            listbox_values.set(data)

    def on_change_selection(event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            data = event.widget.get(index)
            entry_text.set(data)
            check_input()

    def btn_click():
        global login
        global password
        global n
        global t
        global user_login
        global role
        global role_
        global dep
        global date
        global date_
        global reg_sub

        n = int(n_input.get())
        t = int(sleep.get())
        reg_sub = reg.get()
        role = combo_role.get()
        role_ = str(role)
        role = roles_data[role]
        dep = combo_dep.get()
        try:
            dep = dep_data[dep]
        except:
            dep = ''
        date = date_input.get()
        date_ = date_input_.get()
        user = combo_user.get()
        if user:
            sp = re.search(r'[-яА-Я]', user)[0]
            user_login = user.split(sp)[0].replace('\'', '').replace('[', '').replace('{', '').strip()
        else:
            user_login = ''
        login = login_input.get()
        password = pass_input.get()
        login = normal('login')
        password = normal('password')
        rem = remember_value.get()
        if rem == 'Yes':
            login_crypt = cryptocode.encrypt(login, key)
            password_crypt = cryptocode.encrypt(password, key)
            settings.set('autorization', 'avtologin', 'yes')
            settings.set('autorization', 'login', login_crypt)
            settings.set('autorization', 'password', password_crypt)
        else:
            login_crypt = cryptocode.encrypt('paste_login', key)
            password_crypt = cryptocode.encrypt('paste_pass', key)
            settings.set('autorization', 'avtologin', 'no')
            settings.set('autorization', 'login', login_crypt)
            settings.set('autorization', 'password', password_crypt)
        with open('settings.ini', 'w') as configfile:
            settings.write(configfile)
        root.destroy()

    root = Tk()

    roles_data = distr_json('roles.json')
    dep_data = distr_json('dep.json')
    # roles_value = list(roles_data.values())
    roles = list(roles_data.keys())
    dep = list(dep_data.keys())
    users_data = get_users_from_department(df)
    # users_value = list(users_data)
    # users_key = list(users_data.keys())
    # u = zip(users_key, users_value)
    users = list(users_data)  # list(u)
    quantity = ['1', '10', '20', '30', '40', '50']
    remember_value = StringVar()

    # root.bind('<Escape>', exit_from_form)  # кнопка ВЫХОД по нажатию Esc
    root.protocol("WM_DELETE_WINDOW", exit_from_form)  # ВЫХОД по нажатию на закрытие окна

    if os.path.isfile('rosreestr.png'):
        photo = tkinter.PhotoImage(file='rosreestr.png')
        root.iconphoto(False, photo)  # смена иконки
    root['bg'] = 'white'
    # root.resizable(False, False)  # не изменять размеры
    root.title('Форма для заполнения')
    center(root, width, height)  # вызываем функцию центровки окна
    root.attributes('-topmost', 1)  # поверх окон
    # root.wm_attributes('-alpha', 0.7) # прозрачность
    root.geometry(f'{width}x{height}')  # размер и сдвиг в пикселях

    canvas = Canvas(root, height=280, width=580, bg='#EBE8DB')
    canvas.pack()

    frame = Frame(canvas, height=200, width=600, bg='#71D8E8')
    frame.pack(side=TOP, fill='both')

    frame_second = Frame(canvas, height=200, width=570, bg='#71D8E8')
    frame_second.pack(fill='both')
    Label(frame_second, text='количество: ', bg='white', relief='groove', bd=2).pack(side=LEFT, padx=10)
    n_input = ttk.Combobox(frame_second, values=quantity, width=2)
    n_input.pack(side=LEFT)
    n_input.current(1)
    Label(frame_second, text='пауза: ', bg='white', relief='groove', bd=2).pack(side=LEFT, padx=10)
    sleep = Entry(frame_second, bg='white', width=2, relief='sunken', bd=2)
    sleep.pack(side=LEFT)
    sleep.insert(0, '1')

    Label(frame_second, bg='#71D8E8').pack(side=LEFT, padx=10)
    remember = Checkbutton(frame_second, text='запомнить пароль', bg='white', variable=remember_value, offvalue='No',
                           onvalue='Yes', relief='groove', bd=2)
    remember.pack(side=LEFT, padx=10)

    Label(frame_second, text='регион: ', bg='white', relief='groove', bd=2).pack(side=LEFT, padx=10)
    reg = Entry(frame_second, bg='white', width=2, relief='sunken', bd=2)
    reg.pack(side=LEFT)
    reg.insert(0, '72')

    frame_end = Frame(canvas, height=30, width=240, bg='white')
    frame_end.pack(side=BOTTOM, expand=1, fill='both')
    frame_down = Frame(canvas, height=200, width=240, bg='#71D8E8')
    frame_down.pack(side=BOTTOM, expand=1, fill='both')
    btn = Button(frame_down, text='ВВОД', bg='#fff4b2', command=btn_click, relief=tkinter.RAISED, bd=3)
    btn.grid(row=0, column=0, sticky='e', padx=10)
    ex = Button(frame_down, text='ВЫХОД', bg='#F3A476', command=exit_from_form, relief=tkinter.RAISED, bd=3)
    ex.grid(row=0, column=1, sticky='w', padx=10)
    frame_down.grid_rowconfigure(0, minsize=50)
    frame_down.grid_columnconfigure(0, minsize=250)
    frame_down.grid_columnconfigure(1, minsize=250)

    title = Label(frame, text='Введите логин и пароль от ФГИС ЕГРН', bg='gray', relief='ridge')
    title.grid(row=0, column=0, columnspan=2, padx=147)

    Label(frame, text='логин: ', bg='white', relief='groove', bd=2).grid(row=1, column=0, pady=10, sticky='e')
    login_input = Entry(frame, bg='white', relief='sunken', bd=2)
    login_input.grid(row=1, column=1, pady=10, sticky='w', padx=5)
    # flat, groove, raised, ridge, solid, or sunken
    # frame.grid_rowconfigure(2, minsize=5)
    Label(frame, text='пароль: ', bg='white', relief='groove', bd=2).grid(row=2, column=0, stick='e')
    pass_input = Entry(frame, show="*", bg='white', relief='sunken', bd=2)
    pass_input.grid(row=2, column=1, stick='w', padx=5, pady=5)
    login_input.insert(0, cryptocode.decrypt(settings['autorization']['login'], key))
    pass_input.insert(0, cryptocode.decrypt(settings['autorization']['password'], key))

    if settings['autorization']['avtologin'] == 'yes':
        remember_value.set("Yes")
    else:
        remember_value.set("No")

    frame_left = Frame(canvas, height=200, width=240, bg='#71D8E8')
    frame_left.pack(side=LEFT, expand=1, fill='both')
    frame_right = Frame(canvas, height=200, width=240, bg='#71D8E8')
    frame_right.pack(side=RIGHT, expand=1, fill='both')

    Label(frame_right, text='выберите роль: ', bg='gray', relief='ridge').pack(pady=10)
    combo_role = ttk.Combobox(frame_right, values=roles, width=35)
    combo_role.pack()
    combo_role.current(1)

    entry_text = StringVar()
    Label(frame_right, text='выберите пользователя: ', bg='gray', relief='ridge').pack(pady=10)
    combo_user = Entry(frame_right, textvariable=entry_text, relief='sunken', bd=2, width=25)
    combo_user.bind('<KeyRelease>', check_input)
    combo_user.pack()

    listbox_values = Variable()
    listbox = Listbox(frame_right, listvariable=listbox_values, width=25)
    listbox.bind('<<ListboxSelect>>', on_change_selection)
    listbox.pack()
    listbox_values.set(users)

    Label(frame_left, text='выберите отдел: ', bg='gray', relief='ridge').pack(pady=10)
    # ins = Button(frame_left, text='вставить', bg='#fff4b2', command=insert, relief=tkinter.RAISED, bd=3)
    # ins.pack()
    combo_dep = ttk.Combobox(frame_left, values=dep, width=35)
    combo_dep.pack()

    Label(frame_left, text='выберите дату с: ', bg='gray', relief='ridge').pack(pady=10)
    date_input = DateEntry(
        frame_left, width=16, background="magenta3", foreground="white", bd=2, date_pattern='yyy-mm-dd', locale='ru_RU')
    date_input.pack()
    Label(frame_left, text='выберите дату по: ', bg='gray', relief='ridge').pack(pady=10)
    date_input_ = DateEntry(
        frame_left, width=16, background="magenta3", foreground="white", bd=2, date_pattern='yyy-mm-dd', locale='ru_RU')
    date_input_.pack()

    root.mainloop()


if __name__ == '__main__':
    print(return_id())
