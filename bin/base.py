#!/usr/bin/env python
import csv
import functools
import glob
import json
import os
import re
import sys
from peewee import *
from playhouse.postgres_ext import JSONField 
from playhouse.sqlite_ext import SqliteExtDatabase

hosts_piloto = [
    'rp2-piloto-1',
]

db_name = "sqlite_piloto.db"
database = SqliteDatabase(db_name, pragmas=(
    ('foreign_keys', 1),
    ('journal_mode', 'wal'),
    ))

dir_log_piloto = os.environ['HOME'] + "/m/rp2-piloto-1/log"

# SCHEMA DEFINITIONS

class BaseExtModel(Model):
    class Meta:
        database = database

#class Gpsd(BaseExtModel):
#    tstamp = DateTimeTZField(null=True)
#    data = BinaryJSONField()

class Bluelog(BaseExtModel):
    hostname = CharField()
    tstamp = DateField()
    mac = CharField(max_length = 17)
    name = CharField()
    class Meta:
        indexes = (
            (('hostname', 'tstamp', 'mac', 'name'), True),
        )

class Geolocator(BaseExtModel):
    hostname = CharField()
    tstamp = DateField()
    latitude = FloatField() 
    longitude = FloatField() 
    speed = FloatField()
    altitude = FloatField()
    data = JSONField()

# UTILITY FUNCTIONS

tables = [
    Bluelog,
    Geolocator,
    #Gpsd,
]

if __name__ == '__main__':
    pass 
