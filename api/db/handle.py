from peewee import SqliteDatabase, Model

user = 'root'
password = 'root'
db_name = 'peewee_demo.db'

dbhandle = SqliteDatabase(
    db_name,
    # user=user,
    # password=password,
    # host='localhost'
)


class PeeWeeBaseModel(Model):
    class Meta:
        database = dbhandle
