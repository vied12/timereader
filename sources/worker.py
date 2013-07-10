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
# Last mod : 06-Jul-2013
# -----------------------------------------------------------------------------
import jobs
from flask import Flask

app = Flask(__name__)
app.config.from_envvar('TIMEREADER_SETTINGS')

class Worker:

	def __init__(self, async=False):
		self.async = async
		if self.async:
			import redis
			from rq import Queue
			self.queue = Queue(connection=redis.from_url(app.config['REDIS_URL']))

	def run(self, job, *arg, **kwargs):
		__import__('jobs.'+job)
		
		class_name = job.replace('_', ' ').title().replace(' ', '')
		job = eval('jobs.%s.%s()' % (job, class_name))

		if self.async:
			self.run_redis(job, *arg, **kwargs)
		else:
			self.run_synchronously(job, *arg, **kwargs)

	def run_synchronously(self, job, *arg, **kwargs):
		job.run(*arg, **kwargs)

	def run_redis(self, job, *arg, **kwargs):
		result = self.queue.enqueue(job.run, *arg, **kwargs)

# EOF
