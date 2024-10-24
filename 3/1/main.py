from cassandra.cluster import Cluster

from app.helpers import get_from_db, init_db, make_ceed_random

cluster = Cluster(['127.0.0.1'])
session = cluster.connect()

init_db(session)
make_ceed_random(session, 1000)
# get_from_db(session)

print('Ok')
