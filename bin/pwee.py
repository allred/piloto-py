#!/usr/bin/env python
# run ./% --help
# initialize:
# create database piloto
import click
import csv
import glob
import json
import os
import peewee
import re
import sys
from playhouse.postgres_ext import *

database = PostgresqlDatabase(
    'piloto',
)

dir_log_piloto = os.environ['HOME'] + "/m/rp3-piloto-1/log"

# SCHEMA DEFINITIONS

class BaseModel(Model):
    class Meta:
        database = database

class Gpsd(BaseModel):
    class_ = CharField() # this field is "class" in the gpsd json
    tag = CharField()
    device = CharField()
    mode = IntegerField()
    time = DateTimeTZField()
    ept = DecimalField()
    lat = DecimalField()
    lon = DecimalField()
    track = DecimalField()
    speed = DecimalField()

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
        indexes = (
            (('data', 'tstamp'), True),
        )

# UTILITY FUNCTIONS

tables = [
    Bluelog,
    Geolocator,
    Gpsd,
]

def create_tables():
    database.get_conn()
    database.create_tables(tables, safe=True)

def drop_tables():
    database.get_conn()
    database.drop_tables(tables, safe=True)

def list_tables():
    c = database.get_conn().cursor()
    c.execute('''

SELECT nspname || '.' || relname AS "relation",
    pg_size_pretty(pg_relation_size(C.oid)) AS "size"
  FROM pg_class C
  LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
  WHERE nspname NOT IN ('pg_catalog', 'information_schema')
  ORDER BY pg_relation_size(C.oid) DESC
  LIMIT 20;

/*
    select relname, relpages
    from pg_class
    order by relpages desc
    limit 20
*/

/*
SELECT *, pg_size_pretty(total_bytes) AS total
    , pg_size_pretty(index_bytes) AS INDEX
    , pg_size_pretty(toast_bytes) AS toast
    , pg_size_pretty(table_bytes) AS TABLE
  FROM (
  SELECT *, total_bytes-index_bytes-COALESCE(toast_bytes,0) AS table_bytes FROM (
      SELECT c.oid,nspname AS table_schema, relname AS TABLE_NAME
              , c.reltuples AS row_estimate
              , pg_total_relation_size(c.oid) AS total_bytes
              , pg_indexes_size(c.oid) AS index_bytes
              , pg_total_relation_size(reltoastrelid) AS toast_bytes
          FROM pg_class c
          LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
          WHERE relkind = 'r'
  ) a
) a
  ORDER BY total
  -- LIMIT 2
;
*/
    ''')
    print([desc[0] for desc in c.description])
    for r in c:
        print(r)

def load_tables():
    database.get_conn()
    load_bluelog()
    load_geolocator()

def progbar(i, every = 1):
    if i % every == 0:
        print('.', end='', flush=True)

def load_bluelog():
    print("loading bluelog", end='')
    re_skip = re.compile(".*Scan started on.*|.*Scan ended.*|.*\x00.*")
    for i, file in enumerate(glob.glob(dir_log_piloto + "/btoothlog/*.log")):
        #print({'f': file})
        progbar(i, 5)
        for line in open(file, "r", errors='ignore').readlines():
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
            # there is some junk data, try to ensure it looks like json
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
    #click.echo('listing tables')
    list_tables()

@cli.command()
def load():
    #click.echo('loading tables')
    load_tables()

if __name__ == '__main__':
    cli()
