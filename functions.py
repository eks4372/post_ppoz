import pandas as pd
import orm


def make_df_from_xlsx(file, sheet='Лист1'):
    df = pd.read_excel(file, sheet_name=sheet)
    return df


def get_users_from_department(df, department=''):
    if type(df) is dict:
        u_l = []
        if department:
            df = orm.get_users(org_id=department, login=True, name=True)
            # print(type(df))
            # print(df)
            for k in df:
                u_l.append([k, df[k]])
            return u_l
        else:
            for k in df:
                u_l.append([k, df[k]])
            return u_l
    else:
        # df = pd.read_excel(file, sheet_name=sheet)
        if department:
            df = df[df.Организация == float(department)]
            return df[['Логин', 'ФИО']].values
        else:
            return df[['Логин', 'ФИО', 'Организация']].values


def get_department_of_user(df, user):
    if type(df) is dict:
        return orm.User.get(orm.User.logins == user).org_id
    else:
        # df = pd.read_excel(file, sheet_name=sheet)
        df = df[df.Логин == user]
        return df['Организация'].values[0]


def get_role_to_user(df, user):
    if type(df) is dict:
        return orm.User.get(orm.User.logins == user).roles
    else:
        df = df[df.Логин == user]
        return str(df['Роли'].values[0])


def get_fio_from_user(df, user):
    if type(df) is dict:
        return orm.User.get(orm.User.logins == user).fio
    else:
        df = df[df.Логин == user]
        return df['ФИО'].values[0]


if __name__ == '__main__':
    d = {
        '2023-04-03': {'Завьялова Ольга Сергеевна': 25, 'Бетехтина Людмила Викторовна': 22, 'Рябова Юлия Ильдаровна': 0,
                       'Шендель Наталья Павловна': 0, 'Ляхова Елена Александровна': 28,
                       'Швецова Наталья Михайловна': 3}}
    # d1 = {'2023-04-04': {'Завьялова Ольга Сергеевна': 2, 'Бетехтина Людмила Викторовна': 2, 'Рябова Юлия Ильдаровна': 0, 'Шендель Наталья Павловна': 0, 'Ляхова Елена Александровна': 28, 'Швецова Наталья Михайловна': 3}}
    df_ = pd.DataFrame(d)
    df = pd.DataFrame()
    # print(df)
    # print('-'*5)
    # # df_ = pd.concat([df_, pd.DataFrame(d)], ignore_index=False)
    # # df_ = pd.concat([df_, pd.DataFrame(d)], ignore_index=False)
    df_ = df_.join(df)
    print(df_)
