#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Time Reader
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 06-Jul-2013
# Last mod : 03-Feb-2014
# -----------------------------------------------------------------------------
from flask import Flask
import jobs

app = Flask(__name__)
app.config.from_envvar('TIMEREADER_SETTINGS')

class Worker(object):

	def __init__(self, async=False):
		self.async = async
		if self.async:
			import redis
			from rq import Queue
			self.queue = Queue(connection=redis.from_url(app.config['REDIS_URL']))

	def run(self, job, *arg, **kwargs):
		job = jobs.perform_jobs_import(job)()
		if self.async:
			self.run_redis(job, *arg, **kwargs)
		else:
			self.run_synchronously(job, *arg, **kwargs)

	def run_synchronously(self, job, *arg, **kwargs):
		job.run(*arg, **kwargs)

	def run_redis(self, job, *arg, **kwargs):
		self.queue.enqueue(job.run, *arg, **kwargs)

# EOF
