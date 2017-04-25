#!/usr/bin/env python
# run ./% --help
import click
import csv
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

class Bluelog(BaseModel):
  tstamp = DateTimeTZField()
  mac = CharField(max_length = 17) 
  name = CharField()
  class Meta:
    indexes = (
      (('tstamp', 'mac', 'name'), True),
    )

class Geolocator(BaseModel):
  tstamp = DateTimeTZField()
  data = BinaryJSONField()
  class Meta:
    database = database
    indexes = (
      (('data', 'tstamp'), True),
    )

# UTILITY FUNCTIONS

tables = [
  Bluelog,
  Geolocator,
]

def create_tables():
  database.get_conn()
  database.create_tables(tables, safe=True)

def drop_tables():
  database.get_conn()
  database.drop_tables(tables, safe=True) 

def load_tables():
  database.get_conn()
  load_bluelog()
  load_geolocator()

def progbar(i, every = 1): 
  if i % every == 0:
    print('.', end='', flush=True)

def load_bluelog():
  print("loading bluelog", end='')
  re_skip = re.compile(".*Scan started.*|.*Scan ended.*|.*\x00.*")
  for i, file in enumerate(glob.glob(dir_log_piloto + "/btoothlog/*.log")):
    progbar(i, 5)
    for line in open(file, "r").readlines():
      if re_skip.match(line):
        continue 
      for row in csv.reader([line]):
        Bluelog.get_or_create(
          tstamp = row[0],
          mac = row[1],
          name = row[2],
        )
  print("\n")

# TODO: add host when missing
def load_geolocator():
  print("loading geolocator", end='')
  for i, file in enumerate(glob.glob(dir_log_piloto + "/geolocator/*.log")):
    progbar(i)
    for line in open(file, "r").readlines():
      # there is some junk data, ensure it looks like json
      if re.match("^\{", line) == None:
        continue 
      data = json.loads(line)
      Geolocator.get_or_create(
        tstamp = data['time'],
        data = line,
      )
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
