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
from job import Job
import readability
from storage import Article
from flask import Flask
import requests
from worker import Worker


app = Flask(__name__)
app.config.from_envvar('TIMEREADER_SETTINGS')
worker = Worker(async=False)

class RetrieveReadability(Job):

	def run(self, token, user_id):

		rdd = readability.oauth(app.config['READABILITY_CONSUMER_KEY'],
			app.config['READABILITY_CONSUMER_SECRET'], token=token)
		for bookmark in rdd.get_bookmarks():
			url = bookmark.article.url
			worker.run('retrieve_page', url, user_id=user_id, source='readability')

# EOF