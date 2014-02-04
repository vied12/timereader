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
from . import Job, job
from worker import Worker
import readability
from flask import Flask

app = Flask(__name__)
app.config.from_envvar('TIMEREADER_SETTINGS')
worker = Worker(async=False)

@job("RetrieveReadability")
class RetrieveReadability(Job):

	def run(self, token, user_id):

		rdd = readability.oauth(app.config['READABILITY_CONSUMER_KEY'],
			app.config['READABILITY_CONSUMER_SECRET'], token=token)
		for bookmark in rdd.get_bookmarks():
			url = bookmark.article.url
			worker.run('retrieve_page', url, user_id=user_id, source='readability', thematic="readability") # FIXME: thematic sould be specified

# EOF
