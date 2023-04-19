from datetime import datetime, timedelta
from functions import pd
from myfunctions import distr_json
from orm_models import *


def from_xlsx_to_bd(file, model):
    '''если таблица пуста, то импортируем всё прямо из xlsx'''
    if model.get_or_none():
        print(f'таблица {model} содержит данные, импорт отменён')
    else:
        from functions import pd
        df = pd.read_excel(file)
        df.to_sql(name='users', con=conn, if_exists='append', index=False)
        print(f'импорт {file} в {model} завершён')
    del_user_without_role()


def add_users(data):
    '''если в таблице уже есть пользователи, импортируем из xlsx убирая уже существующих'''
    from functions import pd
    df = pd.read_excel(data)
    try:
        df.to_sql(name='users', con=conn, if_exists='append', index=False)
    except:
        print(f'есть уже существующте пользователи, удаляем')
        # df = df[(df.Логин.isin(existing.Логин))]  # это выборка существующих
        existing = pd.read_sql('SELECT *FROM users', conn)
        import numpy as np
        df = df[np.logical_not(df.Логин.isin(existing.Логин))]  # это выборка тех, которых нету
        print(df)
        df.to_sql(name='users', con=conn, if_exists='append', index=False)
    print(f'импорт {data} в {User} завершён')
    del_user_without_role()


def add_number(data, date_request, role):
    with conn:
        for i in data:
            for u in i['responsibleUsers']:
                if u['role'] == role:
                    # fio = u['firstName'] + u['lastName'] + u['secondName']
                    fio = f"{u['lastName']} {u['firstName']} {u['secondName']}"
                    date = u['completionDate']
                    if date is None:
                        date = date_request  # заменяем пустое поле ?
                    # else:
                    #     date = datetime.strptime(u['completionDate'], '%Y-%m-%d %H:%M:%S.%f') - timedelta(hours=5)
            try:
                if role == 'PKURP_REG':
                    num = PacketReg(numbers=i['appealNumber'], status=i['status'], types=i['serviceName'],
                                    registrars=fio, completion_date=date)
                elif role == 'PKURP_KAD':
                    num = PacketKad(numbers=i['appealNumber'], status=i['status'], types=i['serviceName'],
                                    registrars=fio, completion_date=date)
                elif role == 'PKURP_ARC':
                    num = PacketArc(numbers=i['appealNumber'], status=i['status'], types=i['serviceName'],
                                    registrars=fio, completion_date=date)
                elif role == 'PKURP_PREREG':
                    num = PacketPre(numbers=i['appealNumber'], status=i['status'], types=i['serviceName'],
                                    registrars=fio, completion_date=date)
                elif role == 'PKURP_INFO':
                    num = PacketInfo(numbers=i['appealNumber'], status=i['status'], types=i['serviceName'],
                                    registrars=fio, completion_date=date)
                elif role == 'PKURP_EX':
                    num = PacketEx(numbers=i['appealNumber'], status=i['status'], types=i['serviceName'],
                                    registrars=fio, completion_date=date)

                num.save()
            except IntegrityError:
                print(f'обращение {i} уже есть в базе')


def get_info(role, user='', type='', date_from='', date_to='', status=''):
    if role == 'PKURP_REG':
        table = PacketReg
    elif role == 'PKURP_KAD':
        table = PacketKad
    elif role == 'PKURP_ARC':
        table = PacketArc
    elif role == 'PKURP_PREREG':
        table = PacketPre
    elif role == 'PKURP_INFO':
        table = PacketInfo
    elif role == 'PKURP_EX':
        table = PacketEx
    if user and type and not status:
        if not date_to and not date_from:
            r = table.select().where(table.registrars == user, table.types == type)
        elif date_from and not date_to:
            r = table.select().where(table.registrars == user, table.types == type,
                                     table.completion_date >= date_from)
        elif date_to and not date_from:
            r = table.select().where(table.registrars == user, table.types == type,
                                     table.completion_date <= date_to)
        else:
            r = table.select().where(table.registrars == user, table.types == type,
                                     table.completion_date <= date_to, table.completion_date >= date_from)
    elif user and not type and not status:
        if not date_to and not date_from:
            r = table.select().where(table.registrars == user)
        elif date_from and not date_to:
            r = table.select().where(table.registrars == user, table.completion_date >= date_from)
        elif date_to and not date_from:
            r = table.select().where(table.registrars == user, table.completion_date <= date_to)
        else:
            r = table.select().where(table.registrars == user,
                                     table.completion_date <= date_to, table.completion_date >= date_from)
    elif user and type and status:
        if not date_to and not date_from:
            r = table.select().where(table.registrars == user, table.types == type, table.status == status)
        elif date_from and not date_to:
            r = table.select().where(table.registrars == user, table.types == type, table.status == status
                                     , table.completion_date >= date_from)
        elif date_to and not date_from:
            r = table.select().where(table.registrars == user, table.types == type, table.status == status
                                     , table.completion_date <= date_to)
        else:
            r = table.select().where(table.registrars == user, table.types == type, table.status == status,
                                     table.completion_date <= date_to, table.completion_date >= date_from)
    elif user and not type and status:
        if not date_to and not date_from:
            r = table.select().where(table.registrars == user, table.status == status)
        elif date_from and not date_to:
            r = table.select().where(table.registrars == user, table.status == status,
                                     table.completion_date >= date_from)
        elif date_to and not date_from:
            r = table.select().where(table.registrars == user, table.status == status,
                                     table.completion_date <= date_to)
        else:
            r = table.select().where(table.registrars == user, table.status == status,
                                     table.completion_date <= date_to, table.completion_date >= date_from)
    elif not user and type and status:
        if not date_to and not date_from:
            r = table.select().where(table.status == status, table.types == type)
        elif date_from and not date_to:
            r = table.select().where(table.status == status, table.types == type,
                                     table.completion_date >= date_from)
        elif date_to and not date_from:
            r = table.select().where(table.status == status, table.types == type,
                                     table.completion_date <= date_to)
        else:
            r = table.select().where(table.status == status, table.types == type,
                                     table.completion_date <= date_to, table.completion_date >= date_from)
    elif not user and type and not status:
        if not date_to and not date_from:
            r = table.select().where(table.types == type)
        elif date_from and not date_to:
            r = table.select().where(table.types == type, table.completion_date >= date_from)
        elif date_to and not date_from:
            r = table.select().where(table.types == type, table.completion_date <= date_to)
        else:
            r = table.select().where(table.types == type,
                                     table.completion_date <= date_to, table.completion_date >= date_from)
    elif not user and not type and status:
        if not date_to and not date_from:
            r = table.select().where(table.status == status)
        elif date_from and not date_to:
            r = table.select().where(table.status == status, table.completion_date >= date_from)
        elif date_to and not date_from:
            r = table.select().where(table.status == status, table.completion_date <= date_to)
        else:
            r = table.select().where(table.status == status,
                                     table.completion_date <= date_to, table.completion_date >= date_from)
    else:
        if not date_to and not date_from:
            r = table.select()
        elif date_from and not date_to:
            r = table.select().where(table.completion_date >= date_from)
        elif date_to and not date_from:
            r = table.select().where(table.completion_date <= date_to)
        else:
            r = table.select().where(table.completion_date <= date_to, table.completion_date >= date_from)

    return r


def make_xlsx(q, file_name='отчет.xlsx'):
    if '.xlsx' in file_name:
        file_name = file_name
    else:
        file_name = f'{file_name}.xlsx'
    df = pd.DataFrame(list(q.dicts()))
    try:
        df = df.drop(columns=['id'], axis=1)
        df.to_excel(file_name, index=False)
        print(f'файл {file_name} сохранён')
    except:
        print(f'не удалось сохранить выборку \n{df}')


def make_orders(role, dateFrom, dateTo, users, type='', status='', outfile=''):
    dateFrom = datetime.strptime(dateFrom, '%Y-%m-%d')
    dateTo = datetime.strptime(dateTo, '%Y-%m-%d')
    df_t = pd.DataFrame()
    while dateTo >= dateFrom:
        users_on_date = {}
        for user in users:
            # получаем ключ по значению изсловаря (distr_json('roles.json'))
            # print(list(distr_json('roles.json').keys())[list(distr_json('roles.json').values()).index(role)])
            # print(User.get(User.fio == user).roles)
            if list(distr_json('roles.json').keys())[list(distr_json('roles.json').values()).index(role)] not in\
                    User.get(User.fio == user).roles:
                continue
            users_on_date[user] = len(get_info(
                role=role, user=user, type=type, date_from=str(dateFrom)[:10],
                date_to=str(dateFrom)[:10], status=status))
        d = {str(dateFrom)[:10]: users_on_date}
        df = pd.DataFrame(d)
        if df_t.empty:
            df_t = df
        else:
            df_t = df_t.join(df)
        print(f"{dateFrom.strftime('%Y-%m-%d')} готово")
        dateFrom += timedelta(days=1)
    if not outfile:
        outfile = settings['options']['outfile']
    if '.xlsx' in outfile:
        outfile = outfile
    else:
        outfile = f'{outfile}.xlsx'
    try:
        df_t.to_excel(outfile, index=True)
    except:
        print(f'не могу сохранить файл {outfile}.xlsx, пробую сохранить в tmp.xlsx')
        df_t.to_excel('tmp.xlsx', index=True)


def get_users(org_id='', login=False, name=True):
    users = []
    if org_id:
        r = User.select().where(User.org_id == org_id)
    else:
        r = User.select()
    if not login and name:
        for u in r.dicts().execute():
            users.append(u['fio'])
    elif not login and name:
        for u in r.dicts().execute():
            users.append(u['logins'])
    else:
        users = {}
        for u in r.dicts().execute():
            users[u['logins']] = u['fio']  # {'irvpeganova': 'Пеганова Ирина Вячеславовна'
    return users


def del_user_without_role():
    u = User.select().where(User.roles == None)
    for i in u.dicts().execute():
        print(f'отсутствуют роли \n{i}')
    print(f'удалено {User.delete().where(User.roles == None).execute()} записей пользователей')



if __name__ == '__main__':
    # from_xlsx_to_bd('users.xlsx', User)
    # add_users('users.xlsx')
    # u = get_users('72.044')
    # role = 'PKURP_REG'
    # make_orders(role=role, dateFrom='2023-03-01', dateTo='2023-03-10', u)
    # make_orders(role=role, dateFrom='2023-03-01', dateTo='2023-03-10', users=u, status='Приостановление обработки')
    # d = User.get(User.logins == 'animirvoda').org_id
    # print(d)

    # info = get_info('PKURP_REG', 'Ляхова Елена Александровна', date_from='2023-03-01', date_to='2023-03-01', status='Приостановление обработки')
    # print(info)
    # info = get_info('Бетехтина Людмила Викторовна', date_from='2023-03-09', date_to='2023-03-09', status='Приостановление обработки')
    # make_xlsx(info)
    # info =r = Packet.select()
    # print(len(info))
    # for i in info.dicts().execute():
    #     print(i)
    # u = get_users('72.044')
    # print(u)
    # r = PacketReg.select().where(PacketReg.status == )

    # u = User.select().where(User.org_id == '72.044')
    # for i in u.dicts().execute():
    #     print(i['logins'])
    #     print(i['fio'])
    # r = User.get(User.logins == 'avpoletneva').roles
    # print(r)
    # if r == None:
    #     print('N')
    del_user_without_role()

