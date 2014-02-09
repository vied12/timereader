#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Time Reader
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 03-Feb-2014
# Last mod : 03-Feb-2014
# -----------------------------------------------------------------------------
from __future__ import absolute_import
from timereader.jobs import Job, job
from timereader import Worker
from flask import Flask
import twitter
from pprint import pprint as pp

app = Flask(__name__)
app.config.from_envvar('TIMEREADER_SETTINGS')
worker = Worker(async=False)

@job("Retrieve somes links on the Twitter timeline")
class Twitter(Job):

	def run(self, token_id, token_secret):
		api = twitter.Api(
			consumer_key        = app.config.get("TWITTER_CONSUMER_KEY"), 
			consumer_secret     = app.config.get("TWITTER_CONSUMER_SECRET"), 
			access_token_key    = token_id, 
			access_token_secret = token_secret
		)
		timeline = api.GetHomeTimeline(count=200)
		urls = [[u.expanded_url for u in status.urls] for status in timeline if status.urls]
		for url in urls:
			worker.run('retrieve_page', url[0], source='twitter')

# -----------------------------------------------------------------------------
#
# TESTS
#
# -----------------------------------------------------------------------------
import unittest

class TestTwitter(unittest.TestCase):

	def setUp(self):
		self.obj = Twitter()

	def test_run(self):
		self.obj.run(app.config.get("TWITTER_TEST_ACCESS_TOKEN"), app.config.get("TWITTER_TEST_ACCESS_TOKEN_SECRET"))

if __name__ == "__main__":
	# unittest.main()
	suite = unittest.TestLoader().loadTestsFromTestCase(TestTwitter)
	unittest.TextTestRunner(verbosity=2).run(suite)

# EOF
