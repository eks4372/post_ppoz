from peewee import *
import configparser
import os

settings = configparser.ConfigParser()
settings.read('settings.ini', encoding="utf-8")
db_path = settings['db']['path']
# db_path = r'ppoz_loc.db'
if not os.path.isfile(db_path):
    input(f'[ВНИМАНИЕ!] отсутствует вайл базы данных {db_path}, нажмите enter для создания файла ')
conn = SqliteDatabase(db_path)


class BaseModel(Model):
    class Meta:
        database = conn


class User(BaseModel):
    class Meta:
        db_table = 'users'

    # index =AutoField()
    logins = CharField(column_name='Логин', unique=True)
    fio = CharField(column_name='ФИО', )
    org_id = CharField(column_name='Организация', )
    departments = CharField(column_name='Отдел', null=True)
    roles = TextField(column_name='Роли', null=True)


class PacketReg(BaseModel):
    class Meta:
        db_table = 'packets_reg'

    numbers = CharField(unique=True)
    types = CharField()
    status = CharField(null=True)
    # registrars = ForeignKeyField(User, field=User.fio)
    registrars = CharField()
    completion_date = DateField(null=True)


class PacketKad(BaseModel):
    class Meta:
        db_table = 'packets_kad'

    numbers = CharField(unique=True)
    types = CharField()
    status = CharField(null=True)
    # registrars = ForeignKeyField(User, field=User.fio)
    registrars = CharField()
    completion_date = DateField(null=True)


class PacketArc(BaseModel):
    class Meta:
        db_table = 'packets_arc'

    numbers = CharField(unique=True)
    types = CharField()
    status = CharField(null=True)
    # registrars = ForeignKeyField(User, field=User.fio)
    registrars = CharField()
    completion_date = DateField(null=True)


class PacketPre(BaseModel):
    class Meta:
        db_table = 'packets_pre_reg'

    numbers = CharField(unique=True)
    types = CharField()
    status = CharField(null=True)
    # registrars = ForeignKeyField(User, field=User.fio)
    registrars = CharField()
    completion_date = DateField(null=True)


class PacketInfo(BaseModel):
    class Meta:
        db_table = 'packets_info'

    numbers = CharField(unique=True)
    types = CharField()
    status = CharField(null=True)
    # registrars = ForeignKeyField(User, field=User.fio)
    registrars = CharField()
    completion_date = DateField(null=True)


class PacketEx(BaseModel):
    class Meta:
        db_table = 'packets_ex'

    numbers = CharField(unique=True)
    types = CharField()
    status = CharField(null=True)
    # registrars = ForeignKeyField(User, field=User.fio)
    registrars = CharField()
    completion_date = DateField(null=True)


with conn:
    conn.create_tables([User, PacketReg, PacketPre, PacketArc, PacketKad, PacketInfo, PacketEx])
