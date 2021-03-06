#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Time Reader
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 07-Jul-2013
# Last mod : 07-Jul-2013
# -----------------------------------------------------------------------------
from job import Job
from storage import Article
from flask import Flask
import requests

app = Flask(__name__)
app.config.from_envvar('TIMEREADER_SETTINGS')

class RetrievePage(Job):

	def run(self, url, thematic=None, user_id=None, source=None):
		if not (url.startswith("http://") or url.startswith("https://")):
			url = "http://%s" % url
		# parse the web page
		res = requests.get("http://www.readability.com/api/content/v1/parser?url=%s&token=%s" % 
			(url, app.config['READABILITY_PARSER_TOKEN']))
		parsed  = res.json()
		# save the article
		article = Article()
		article.title       = parsed['title']
		article.date        = parsed['date_published']
		article.content     = parsed['content']
		article.summary     = parsed['excerpt']
		article.link        = parsed['url']
		article.domain      = parsed['domain']
		article.count_words = parsed['word_count']
		article.user        = user_id
		article.thematic    = thematic
		article.type        = source
		article.save()

# EOF