#!/usr/bin/env python
# run ./% --help
import click
import glob
import json
import os
import peewee
import re
from playhouse.postgres_ext import *

database = PostgresqlDatabase(
  'piloto',
)

dir_log_piloto = os.environ['HOME'] + "/m/rp3-piloto-1/log"

# SCHEMA DEFINITIONS

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

# UTILITY FUNCTIONS

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

def load_tables():
  load_geolocator()

def load_geolocator():
  print("loading geolocator", end='')
  database.get_conn()
  index = 0
  for file in glob.glob(dir_log_piloto + "/geolocator/*.log"):
    for line in open(file, "r").readlines():
      # there is some junk data, ensure it looks like json
      if re.match("^\{", line) == None:
        continue 
      data = json.loads(line)
      Geolocator.get_or_create(
        data=line,
        tstamp = data['time']
      )
      if index % 1000 == 0:
        print('.', end='', flush=True)
      index += 1
  print("\n")

# COMMANDS ###################################################################

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

@cli.command()
def load():
  #click.echo('loading tables')
  load_tables()

if __name__ == '__main__':
  cli()
