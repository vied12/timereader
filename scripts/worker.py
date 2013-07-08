#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Time Reader
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 08-Jul-2013
# Last mod : 08-Jul-2013
# -----------------------------------------------------------------------------
import os

import redis
from rq import Worker, Queue, Connection
from flask import Flask

app = Flask(__name__)
app.config.from_pyfile("../settings.cfg")

listen = ['high', 'default', 'low']
conn   = redis.from_url(app.config['REDIS_URL'])

if __name__ == '__main__':
	with Connection(conn):
		worker = Worker(map(Queue, listen))
		worker.work()

# EOF
