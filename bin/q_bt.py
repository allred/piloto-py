#!/usr/bin/env python
from base import *

x = Geolocator.select().where(Geolocator.hostname == 'rp2-piloto-1')
for y in x:
    print(y.speed)

