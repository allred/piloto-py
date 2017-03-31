#!/usr/bin/env python
from peewee import *
from playhouse.postgres_ext import *

database = PostgresqlDatabase(
  'piloto',
)

class BaseModel(Model):
  class Meta:
    database = database

class Geolocator(BaseModel):
  data = BinaryJSONField()
  tstamp = DateTimeTZField()
  class Meta:
    database = database
    indexes = (
      (('data', 'tstamp'), True),
    )

def create_tables():
  database.get_conn()
  database.create_tables([
    Geolocator,
  ], safe=True)

def drop_tables():
  database.get_conn()
  database.drop_tables([
    Geolocator,
  ], safe=True)

if __name__ == '__main__':
  drop_tables()
  create_tables()
  pass
