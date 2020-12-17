#!/usr/bin/env python
# run ./% --help
import click
import csv
import glob
import json
import os
import re
import sys
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase

db_name = "piloto_sqlite.db"
database = SqliteDatabase(db_name, pragmas=(
    ('foreign_keys', 1),
    ('journal_mode', 'wal'),
    ))

dir_log_piloto = os.environ['HOME'] + "/m/rp3-piloto-1/log"

# SCHEMA DEFINITIONS

class BaseExtModel(Model):
    class Meta:
        database = database

#class Gpsd(BaseExtModel):
#    tstamp = DateTimeTZField(null=True)
#    data = BinaryJSONField()

class Bluelog(BaseExtModel):
    tstamp = DateField()
    mac = CharField(max_length = 17)
    name = CharField()
    class Meta:
        indexes = (
            (('tstamp', 'mac', 'name'), True),
        )

#class Geolocator(BaseExtModel):
#    tstamp = DateTimeTZField()
#    data = BinaryJSONField()

# UTILITY FUNCTIONS

tables = [
    Bluelog,
    #Geolocator,
    #Gpsd,
]

def create_tables():
    database.connection()
    database.create_tables(tables, safe=True)

def drop_tables():
    database.connection()
    database.drop_tables(tables, safe=True)

def list_tables():
    c = database.connection().cursor()
    c.execute('''
SELECT
    name
FROM
    sqlite_master
WHERE
    type = 'table' AND
    name NOT LIKE 'sqlite_%'
    ''')
    print([desc[0] for desc in c.description])
    for r in c:
        print(r)

def load_tables():
    database.connection()
    load_bluelog()
    load_geolocator()
    load_gpsd()

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

def load_gpsd():
    print("loading gpsd", end='')
    for i, file in enumerate(glob.glob(dir_log_piloto + "/*.gps")):
        progbar(i)
        for line in open(file, "r").readlines():
            try:
                data_d = json.loads(line)
            except:
                print('x', end='', flush=True)
                continue
            Gpsd.create(
                tstamp = data_d.get("time", "1970-01-01T00:00:00.000Z"),
                data = data_d,
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

@cli.command()
def reload():
    drop_tables()
    create_tables()
    load_tables()

@cli.command()
def l_gpsd():
    load_gpsd()

if __name__ == '__main__':
    cli()
