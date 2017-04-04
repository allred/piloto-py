#!/usr/bin/env python
# run ./% --help
import click
import peewee
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

@click.group()
def cli():
  pass

@cli.command()
def create():
  click.echo('creating tables')
  create_tables()

@cli.command()
def drop():
  click.echo('dropping tables')
  drop_tables()

@cli.command()
def list():
  click.echo('list goes here')

if __name__ == '__main__':
  cli()
