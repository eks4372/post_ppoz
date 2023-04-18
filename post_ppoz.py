import functions
import myfunctions
from selenium import webdriver
from requestium import Session
from time import sleep
import configparser
import sys
from orm import add_number
from gui_reassing import return_id
from datetime import datetime, timedelta

settings = configparser.ConfigParser()
settings.read('settings.ini', encoding="utf-8")

all_user = settings['options']['all_user']

gui_data = return_id()
login = gui_data[0]
password = gui_data[1]
t = int(gui_data[3])
if t <= 0:
    t = 0
dateFrom = datetime.strptime(gui_data[7], '%Y-%m-%d')
dateTo = datetime.strptime(gui_data[10], '%Y-%m-%d')
region = settings['region']['reg']  # Субъект ФР
reg_sub = gui_data[11]  # Субъект объекта недвижимости
role = gui_data[5]
department = gui_data[6]
user = gui_data[4]
n = gui_data[2]
df = gui_data[8]
role_ = gui_data[9]
users = []
r = True
df_t = functions.pd.DataFrame()

if not department:
    department = functions.get_department_of_user(df, user)
if not user and department:
    users = functions.get_users_from_department(df, department)
if role and user:
    if role_ not in functions.get_role_to_user(df, user):
        print(f'[ВНИМАНИЕ!] пользователь {functions.get_fio_from_user(df, user)} не имеет выбранной роли {gui_data[9]}')
        a = input(f'надмите "enter" для продолжение или введите любой символ для изменения решения : ')
        if a:
            r = False
if dateTo.strftime('%Y-%m-%d') < dateFrom.strftime('%Y-%m-%d') \
        or dateTo.strftime('%Y-%m-%d') > datetime.now().strftime('%Y-%m-%d') \
        or dateFrom.strftime('%Y-%m-%d') > datetime.now().strftime('%Y-%m-%d'):
    print('даты выбраны некорректно !')
    r = False

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
url = 'http://ppoz-service-bal-01.prod.egrn:9001/#/administration'
executable_path = settings['path']['executable_path']
browser = webdriver.Chrome(options=options, executable_path=executable_path)
print('start')
# now = datetime.datetime.now().strftime("%d-%m-%Y %H_%M")
# ext = 'txt'
# d = functions.make_dir('result_logs')
# fname = f'{d}\\{now}.{ext}'
# work_file = open(fname, "w+")
# work_file.close()
s = Session(driver=browser)
s.driver.get(url)
sleep(1)
if "ВОЙТИ" in browser.page_source:
    print("страница логина")
    myfunctions.logon(url, browser, login, password)
    sleep(1)
if browser.current_url != url:
    print(browser.current_url)
    print("Что-то пошло не так ((")
    # browser.get(url)
    sleep(5)
    if browser.current_url != url:
        print(browser.current_url)
        print("Походу не работает сайт ((")
        sys.exit()
    elif "ВОЙТИ" in browser.page_source:
        print("страница логина")
        myfunctions.logon(url, browser, login, password)
sleep(1)
s.transfer_driver_cookies_to_session()


def get_total_number(dateFrom, dateTo, region, role, department, user, reg_sub, n=50):
    i = 0
    num_on_page = 1
    total = 0
    while num_on_page != 0:
        data = {
            "pageNumber": i,
            "pageSize": n,
            "decisionDate": {
                "dateFrom": dateFrom,
                "dateTo": dateTo
            },
            "objectRegions": [
                region
            ],
            "subjectRF": [
                reg_sub
            ],
            "executorRoles": [
                role
            ],
            "executorDepartments": [
                department
            ],
            "executors": [
                user
            ]
        }

        # print(data)
        post = s.post('http://ppoz-service-bal-01.prod.egrn:9001/manager/requests', json=data)
        # print(post.text)
        # print(post.status_code)
        # print(post.json())
        # print(post.json()['requests'])
        print(dateFrom)
        add_number(post.json()['requests'], dateFrom, role)  # запись в БД
        print(f'[INFO] запрос по пользователю с логином {user}')
        if 200 <= post.status_code < 400:
            print(f'[INFO] статус запроса : OK')
            num_on_page = len(post.json()['requests'])
            print(f'[INFO] количество обращений на странице : {num_on_page}')
            total += num_on_page
            i += 1
        else:
            print(f'[ERROR] что-то пошло не так код ответа {post.status_code}')
            print(post.text)
            sleep(10)
    print(f'[INFO] количество обращений пользователя {functions.get_fio_from_user(df, user)} : {total}')
    return total


while True:
    while dateTo >= dateFrom:
        if r:
            if not user and department:
                users_on_date = {}
                for u in users:
                    # print(u)
                    # print(functions.get_role_to_user(df, u[0]))
                    if functions.get_role_to_user(df, u[0]) and role_ not in functions.get_role_to_user(df, u[0]) and\
                            all_user != 'yes':
                        print(
                            f'[ВНИМАНИЕ!] пользователь'
                            f' {functions.get_fio_from_user(df, u[0])} не имеет выбранной роли {gui_data[9]}')
                        continue
                    number = get_total_number(
                        n=n, dateFrom=str(dateFrom), dateTo=str(dateFrom), region=region, role=role,
                        department=department, user=u[0], reg_sub=reg_sub)
                    sleep(t)
                    users_on_date[u[1]] = number

                d = {str(dateFrom)[:10]: users_on_date}
                print(d)
                df_ = functions.pd.DataFrame(d)
                # print(df_)
                if df_t.empty:
                    df_t = df_
                else:
                    df_t = df_t.join(df_)
                # print(df_t)
                outfile = settings['options']['outfile']
                if settings['options']['fast_exel'] == 'yes':
                    try:
                        df_t.to_excel(f'{outfile}.xlsx', index=True)
                    except:
                        print(f'не могу сохранить файл {outfile}.xlsx, пробую сохранить в tmp.xlsx')
                        df_t.to_excel('tmp.xlsx', index=True)

            else:
                number = get_total_number(
                    n=n, dateFrom=str(dateFrom), dateTo=str(dateFrom), region=region, role=role, department=department,
                    user=user, reg_sub=reg_sub)
                print(f'всего обращений по пользователю : {number}')
        print(f"{dateFrom.strftime('%Y-%m-%d')} готово")
        dateFrom += timedelta(days=1)

    gui_data = return_id()
    r = True
    if not gui_data:
        break
    login = gui_data[0]
    password = gui_data[1]
    t = int(gui_data[3])
    if t <= 0:
        t = 0
    dateFrom = datetime.strptime(gui_data[7], '%Y-%m-%d')
    dateTo = datetime.strptime(gui_data[10], '%Y-%m-%d')
    region = settings['region']['reg']  # Субъект ФР
    reg_sub = gui_data[11]  # Субъект объекта недвижимости
    role = gui_data[5]
    department = gui_data[6]
    user = gui_data[4]
    n = gui_data[2]
    df = gui_data[8]
    role_ = gui_data[9]
    users = []
    df_t = functions.pd.DataFrame()
    if not department:
        department = functions.get_department_of_user(df, user)
    if not user and department:
        users = functions.get_users_from_department(df, department)
    if role and user:
        if gui_data[9] not in functions.get_role_to_user(df, user):
            print(
                f'[ВНИМАНИЕ!] пользователь {functions.get_fio_from_user(df, user)}'
                f' не имеет выбранной роли {gui_data[9]}')
            a = input(f'надмите "enter" для продолжение или введите любой символ для изменения решения : ')
            if a:
                r = False
    if dateTo.strftime('%Y-%m-%d') < dateFrom.strftime('%Y-%m-%d') \
            or dateTo.strftime('%Y-%m-%d') > datetime.now().strftime('%Y-%m-%d') \
            or dateFrom.strftime('%Y-%m-%d') > datetime.now().strftime('%Y-%m-%d'):
        print('даты выбраны некорректно !')
        r = False

browser.quit()
