#!/usr/bin/env python
from peewee import *
from playhouse.postgres_ext import JSONField
from playhouse.sqlite_ext import SqliteExtDatabase

db_name = "sqlite_piloto.db"
database = SqliteDatabase(db_name, pragmas=(
    ('foreign_keys', 1),
    ('journal_mode', 'wal'),
    ))

class BaseExtModel(Model):
    class Meta:
        database = database

class Geolocator(BaseExtModel):
    hostname = CharField()
    tstamp = DateField()
    data = JSONField()

#x = Geolocator.get(Geolocator.hostname == 'rp2-piloto-1')
#print(x)

x = Geolocator.select().where(Geolocator.hostname == 'rp2-piloto-1')
for y in x:
    print(y.data)

