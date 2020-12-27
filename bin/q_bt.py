#!/usr/bin/env python
#import os, sys
#sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
from base import *

#x = Geolocator.select().where(Geolocator.hostname == 'rp2-piloto-1')
#for y in x:
#    print(y.speed)

q = (
        Bluelog.select(
            Bluelog.name,
            fn.Count(Bluelog.name).alias('count')
        ).where(
            Bluelog.hostname == 'rp2-piloto-1'
        )
        .group_by(Bluelog.name)
        .order_by(SQL('count').asc())
    )
for r in q:
    #print(r.tstamp, r.name)
    print(r.name, r.count)

#query = (User
#         .select(User, fn.Count(Tweet.id).alias('count'))
#         .join(Tweet, JOIN.LEFT_OUTER)
#         .group_by(User))


