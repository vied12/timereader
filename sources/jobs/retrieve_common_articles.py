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
from storage import Article
from flask import Flask
from time import mktime
from datetime import datetime
import requests
import feedparser

CSV_SEPARATOR = ","

class RetrieveCommonArticles(Job):

	def run(self, target):
		sources = self.__get_source(target)
		for source in sources:
			articles = []
			if source['type'] == 'rss':
				articles += self.__scrape_rss(source)
			for article in articles:
				self.__save_article(article)

	def __get_source(self, target):
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
					title    = article['title'],
					date     = datetime.fromtimestamp(mktime(article['published_parsed'])),
					content  = article['content'][0]['value'],
					summary  = article['summary'],
					link     = article['link'],
					thematic = source['thematic'])
				result.append(entry)
			except KeyError as e:
				# TODO: Logs
				# print e, article
				pass
		return result

	def __save_article(self, article):
		""" save an article if it doesn't exist """
		article.count_words = len(article.content.split())
		article.save()

# EOF
