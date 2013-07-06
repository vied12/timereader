#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Time Reader
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : proprietary journalism++
# -----------------------------------------------------------------------------
# Creation : 12-Jun-2013
# Last mod : 18-Jun-2013
# -----------------------------------------------------------------------------

from pymongo import MongoClient
from flask import Flask
from pprint import pprint as pp
import bson

app = Flask(__name__)
app.config.from_pyfile("../settings.cfg")

def get_collection(collection):
	client = MongoClient(app.config['MONGO_HOST'])
	db     = client[app.config['MONGO_DB']]
	return db[collection]

class Station:

	@classmethod
	def get(self, name=None):
		stations = get_collection('stations')
		if not name:
			return stations.find()
		return stations.find({"name":{'$regex':"^%s" % name, "$options": "-i"}})

class Article:

	@classmethod
	def get(self, limit=0, sort=True, **karg):
		# support for thematics filter
		if 'thematics' in karg and karg['thematics']:
			assert type(karg['thematics']) == list, "thematics must be a list"
			karg['thematic'] = {"$in" : karg['thematics']}
		if 'thematics' in karg: del karg['thematics']
		# support for user's articles
		if 'user' in karg and karg['user']:
			# delete the filter by thematic
			# NOTE: sould be optionable
			if 'thematic' in karg:
				del karg['thematic']
		if "id" in karg:
			return get_collection("articles").find_one({"_id": bson.ObjectId(oid=str(karg['id']))})
		articles = get_collection('articles')
		criteria = {k:karg[k] for k in karg if karg[k] != None}
		if sort:
			return articles.find(criteria, limit=limit).sort("count_words", 1)
		else:
			return articles.find(criteria, limit=limit)

	@classmethod
	def get_closest(self, count_words, limit=1, silent=True, **karg):
		articles     = get_collection('articles')
		words        = count_words
		karg['sort'] = False
		# below
		karg['count_words'] = {"$lte": count_words}
		closestBelow        = list(self.get(limit=limit, **karg).sort("count_words", -1))
		karg['count_words'] = {"$gt": count_words}
		# above
		closestAbove        = list(self.get(limit=limit, **karg).sort("count_words", 1))
		results             = closestAbove + closestBelow
		# add delta parameter
		for i, result in enumerate(results):
			result['delta'] = abs(count_words - result['count_words'])
			if silent:
				del result['content']
		# sorting
		results = sorted(results, key=lambda k: k['delta'])
		return results[:limit]

if __name__ == "__main__":
	pp(list(Article.get_closest(400, limit=10,)))
	# pp([_['delta'] for _ in list(Article.get_closest(400, limit=10,))])