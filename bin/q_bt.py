#!/usr/bin/env python
#import os, sys
#sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
from base import *

#x = Geolocator.select().where(Geolocator.hostname == 'rp2-piloto-1')
#for y in x:
#    print(y.speed)

q = Bluelog.select().where(Bluelog.hostname == 'rp2-piloto-1')
for r in q:
    print(r.tstamp, r.name)
