#!/usr/bin/env python
# run ./% --help
import click
from base import *

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
    for h in hosts_piloto:
        load_bluelog(h)
        load_geolocator(h)
        #load_gpsd(h)

def progbar(i, every = 1):
    if i % every == 0:
        print('.', end='', flush=True)

def load_bluelog(hostname):
    num_skipped = 0
    num_loaded = 0
    print(f"loading bluelog for {hostname}", end='')
    re_skip = re.compile(".*Scan started on.*|.*Scan ended.*|.*\x00.*")
    for i, file in enumerate(glob.glob(dir_log_piloto + "/btoothlog/*.log")):
        progbar(i, 5)
        for line in open(file, "r", errors='ignore').readlines():
            if len(line) < 2:
                num_skipped += 1
                continue
            if re_skip.match(line):
                num_skipped += 1
                continue
            for row in csv.reader([line]):
                tstamp = row[0].translate({ord(i): None for i in '[]'})
                Bluelog.get_or_create(
                    hostname = hostname,
                    tstamp = tstamp,
                    mac = row[1],
                    name = row[2],
                )
                num_loaded += 1
    print(f" skipped {num_skipped}/{num_loaded}", end='')
    print("\n")

# TODO: add host when missing
def load_geolocator(hostname):
    num_skipped = 0
    print(f"loading geolocator for {hostname}", end='')
    for i, file in enumerate(glob.glob(dir_log_piloto + "/geolocator/*.log")):
        progbar(i)
        for line in open(file, "r").readlines():
            # there is some junk data, try to ensure it looks like json
            if re.match("^\{", line) == None:
                num_skipped += 1
                continue
            data = json.loads(line)
            #print(data['data'])
            Geolocator.get_or_create(
                hostname = hostname,
                tstamp = data['time'],
                latitude = data['data']['lat'],
                longitude = data['data']['lon'],
                speed = data['data']['speed'],
                altitude = data['data']['altitude'],
                data = data['data'],
            )
    print(f" skipped {num_skipped}", end='')
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
