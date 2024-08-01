from peewee import Model, PrimaryKeyField, CharField

from api.db.handle import PeeWeeBaseModel


class ProjectStat(PeeWeeBaseModel):
    id = PrimaryKeyField(null=False)
    url = CharField(max_length=100)

    class Meta:
        db_table = "projectstat"
