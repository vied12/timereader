#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Time Reader
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 12-Jun-2013
# Last mod : 18-Jun-2013
# -----------------------------------------------------------------------------

from pymongo import MongoClient
from flask import Flask
from pprint import pprint as pp
import bson
import datetime

app = Flask(__name__)
app.config.from_envvar('TIMEREADER_SETTINGS')


class Model(object):

	def __init__(self, **kwargs):
		# default attributes
		self._id         = None
		self.created_date = datetime.datetime.now()
		# add other attributes from kwargs
		for key, value in kwargs.items():
			setattr(self, key, value)

	@property
	def collection(self):
		client   = MongoClient(app.config['MONGO_HOST'])
		db       = client[app.config['MONGO_DB']]
		# return the relative mongodb collection
		collection = db[self.__class__.__name__.lower()]
		return collection

	def save(self):
		# check if the model exists already
		previous_model = None
		# keep only existing attributes
		attributes = filter(lambda _:_[1] != None, self.__dict__.items())
		if self._id:
			previous_model = self.collection.find(dict(_id=self._id))
			self.collection.save(dict(previous_model.items() + attributes))
		# save the model
		else:
			pp(attributes)
			self.collection.insert(dict(attributes))

# -----------------------------------------------------------------------------
#
#    ARTICLE
#
# -----------------------------------------------------------------------------
class Article(Model):

	def __init__(self, **kwargs):
		super(Article, self).__init__(**kwargs)
		self.title        = None
		self.date         = None
		self.content      = None
		self.summary      = None
		self.link         = None
		self.thematic     = None
		self.user         = None
		self.count_words  = None
		self.type         = None

	def save(self):
		if not self.count_words or self.count_words == 0:
			self.count_words = len(self.content.split())
		super(Article, self).save()

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
			return Article.get_collection().find_one({"_id": bson.ObjectId(oid=str(karg['id']))})
		articles = Article.get_collection()
		criteria = {k:karg[k] for k in karg if karg[k] != None}
		if sort:
			return articles.find(criteria, limit=limit).sort("count_words", 1)
		else:
			return articles.find(criteria, limit=limit)

	@classmethod
	def get_closest(self, count_words, limit=1, silent=True, **karg):
		articles     = Article.get_collection()
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

# -----------------------------------------------------------------------------
#
#    USER
#
# -----------------------------------------------------------------------------
class User(Model):

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		self.username = None
		self.password = None
		self.email    = None

# TEST
if __name__ == "__main__":
	pp(list(Article.get_closest(400, limit=10,)))
	# pp([_['delta'] for _ in list(Article.get_closest(400, limit=10,))])