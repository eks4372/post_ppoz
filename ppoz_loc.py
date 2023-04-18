import tkinter.messagebox
from tkinter import *
from tkinter import ttk
from tkcalendar import Calendar, DateEntry
import os.path
import configparser
import orm
from functions import distr_json, get_users_from_department
from orm import get_users
from tkinter import filedialog

settings = configparser.ConfigParser()
settings.read('settings.ini')

width = 580
height = 420

df = get_users(login=True, name=True)


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


exit_flag = False


def user_to_bd():
    filepath = filedialog.askopenfilename()
    if filepath != "":
        orm.from_xlsx_to_bd(filepath, orm.User)


def add_user_from_file():
    filepath = filedialog.askopenfilename()
    if filepath != "":
        orm.add_users(filepath)


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

    def make_order():
        role = combo_role.get()
        role = roles_data[role]
        type = type_input.get()
        status = status_input.get()
        date = date_input.get()
        date_ = date_input_.get()
        user = combo_user.get()
        if user:
            user = user.split('{')[1][:-1]
        else:
            user = ''
        filepath = filedialog.asksaveasfilename()
        if filepath != "":
            orm.make_xlsx(orm.get_info(role=role, user=user, type=type, date_from=date, date_to=date_, status=status),
                          file_name=filepath)

    def make_total():
        role = combo_role.get()
        role = roles_data[role]
        type = type_input.get()
        status = status_input.get()
        date = date_input.get()
        date_ = date_input_.get()
        dep = combo_dep.get()
        try:
            dep = dep_data[dep]
        except:
            dep = ''
        filepath = filedialog.asksaveasfilename()
        if filepath != "":
            orm.make_orders(
                role=role, dateFrom=date, dateTo=date_, users=orm.get_users(org_id=dep),
                type=type, status=status, outfile=filepath)

    root = Tk()

    roles_data = distr_json('roles.json')
    dep_data = distr_json('dep.json')
    roles = list(roles_data.keys())
    dep = list(dep_data.keys())
    users_data = get_users_from_department(df)
    users = list(users_data)  # list(u)
    types = list(distr_json('types.json').keys())
    status = list(distr_json('status.json').keys())

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
    Label(frame_second, text='тип обращения: ', bg='white', relief='groove', bd=2).pack(side=LEFT, padx=10)
    type_input = ttk.Combobox(frame_second, values=types, width=20)
    type_input.pack(side=LEFT)
    type_input.current(0)

    Label(frame_second, bg='#71D8E8').pack(side=LEFT, padx=10)
    Label(frame_second, text='статус обращения: ', bg='white', relief='groove', bd=2).pack(side=LEFT, padx=10)
    status_input = ttk.Combobox(frame_second, values=status, width=20)
    status_input.pack(side=LEFT, padx=10)
    status_input.current(0)

    frame_end = Frame(canvas, height=30, width=240, bg='white')
    frame_end.pack(side=BOTTOM, expand=1, fill='both')
    frame_down = Frame(canvas, height=200, width=240, bg='#71D8E8')
    frame_down.pack(side=BOTTOM, expand=1, fill='both')
    btn_order = Button(frame_down,
                       text='отчёт по пользователю', bg='#fff4b2', command=make_order, relief=tkinter.RAISED, bd=3)
    btn_order.grid(row=0, column=0, sticky='e')
    btn_total = Button(frame_down,
                       text='выгрузить сводный отчет', bg='#F3A476', command=make_total, relief=tkinter.RAISED, bd=3)
    btn_total.grid(row=0, column=1, sticky='w', padx=75)
    ex = Button(frame_down, text='ВЫХОД', bg='#F3A476', command=exit_from_form, relief=tkinter.RAISED, bd=3)
    ex.grid(row=1, column=1, sticky='w', padx=10)
    frame_down.grid_rowconfigure(0, minsize=50)
    frame_down.grid_columnconfigure(0, minsize=250)
    frame_down.grid_columnconfigure(1, minsize=250)

    title = Label(frame, text='Введите данные для запроса', bg='gray', relief='ridge')
    title.grid(row=0, column=0, columnspan=2, padx=210)

    Label(frame, text='загрука пользователей в пустую базу: ', bg='white', relief='groove', bd=2).grid(row=1, column=0,
                                                                                                       pady=10,
                                                                                                       sticky='e')
    open_button = ttk.Button(frame, text="Открыть файл", command=user_to_bd)
    open_button.grid(row=1, column=1, pady=10, sticky='w', padx=5)

    Label(frame, text='добавить пользователей из файла  ', bg='white', relief='groove', bd=2).grid(row=2, column=0,
                                                                                                   stick='e')
    add_button = ttk.Button(frame, text="Открыть файл", command=add_user_from_file)
    add_button.grid(row=2, column=1, stick='w', padx=5, pady=5)

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
    print(form())
