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
# Last mod : 12-Jun-2013
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
	def get(self, limit=0, **karg):
		if "id" in karg:
			return get_collection("articles").find_one({"_id": bson.ObjectId(oid=str(karg['id']))})
		articles = get_collection('articles')
		criteria = {k:karg[k] for k in karg if karg[k] != None}
		return articles.find(criteria, limit=limit).sort("count_words", 1)

	@classmethod
	def get_closest(self, count_words, user=None, thematic=None, limit=1, silent=True):
		articles = get_collection('articles')
		words    = count_words
		loc = {
			"user"       : user,
			"thematic"   : thematic,
			"count_words": {"$lte": words},
		}
		criteria     = {k:loc[k] for k in loc if loc[k] != None}
		closestBelow = list(articles.find(criteria, limit=limit).sort("count_words", -1))
		criteria["count_words"] = {"$gt": words}
		closestAbove = list(articles.find(criteria, limit=limit).sort("count_words", 1))
		results = closestAbove + closestBelow
		# add delta parameter
		for i, result in enumerate(results):
			result['delta'] = abs(count_words - result['count_words'])
			if silent:
				del result['content']
			results[i] = result
		# sorting
		results = sorted(results, key=lambda k: k['delta']) 
		return results[:limit]

if __name__ == "__main__":
	pp(list(Article.get_closest(100, limit=2)))