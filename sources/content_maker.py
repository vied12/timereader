#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : TimeReader
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : MIT Licence
# -----------------------------------------------------------------------------
# Creation : 10-Jun-2013
# Last mod : 10-Jun-2013
# -----------------------------------------------------------------------------

""" 

"""

from pprint import pprint as pp
from time import mktime
from datetime import datetime
import feedparser
import requests

CSV_SEPARATOR = ","

class Article:
	def __init__(self, title=None, date=None, content=None, summary=None, link=None):
		self.title   = title
		self.date    = date
		self.content = content
		self.summary = summary
		self.link    = link

class ContentMaker:
	
	def __init__(self, collection, target):
		self.collection = collection
		self.sources    = self.__get_sources(target)

	def start(self):
		for source in self.sources:
			articles = []
			if source['type'] == 'rss':
				articles += self.__scrape_rss(source)
			for article in articles:
				self.__save_article(article)

	def __get_sources(self, target):
		""" From a google calc, return a list of sources """
		sources = []
		req = requests.get(target)
		lines  = req.text.split('\n')
		header = lines[0].split(CSV_SEPARATOR)
		for line in lines[1:]:
			source = {}
			cells  = line.split(CSV_SEPARATOR)
			for i, cell in enumerate(cells):
				source[header[i]] = cell
			sources.append(source)
		return sources

	def __scrape_rss(self, source):
		""" scape a rss source, return a list of article """
		result = []
		document = feedparser.parse(source['target'])
		for article in document['entries']:
			try:
				entry = Article(
					title   = article['title'],
					date    = datetime.fromtimestamp(mktime(article['published_parsed'])),
					content = article['content'][0]['value'],
					summary = article['summary'],
					link    = article['link'])
				result.append(entry)
			except KeyError as e:
				# TODO: Logs
				# print e, article
				pass
		return result

	def __save_article(self, article):
		""" save an article if it doesn't exist """
		article = article.__dict__
		article['count_words'] = len(article['content'].split())
		self.collection.insert(article)

# EOF
