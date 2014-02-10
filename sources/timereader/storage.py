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
# Last mod : 10-Feb-2014
# -----------------------------------------------------------------------------

from pymongo import MongoClient
from flask import Flask
from pprint import pprint as pp
import bson
import datetime

app = Flask(__name__)
app.config.from_envvar('TIMEREADER_SETTINGS')

class classproperty(property):

	"""
	http://stackoverflow.com/a/1383402
	"""

	def __get__(self, cls, owner):
		return self.fget.__get__(None, owner)()

class Model(object):
	"""
	Base Model for a storable entity
	"""

	DATABASE = app.config['MONGO_DB']

	def __init__(self, **kwargs):
		# default attributes
		self._id         = None
		self.created_date = datetime.datetime.now()
		# add other attributes from kwargs
		for key, value in kwargs.items():
			setattr(self, key, value)

	@classproperty
	@classmethod
	def collection(klass):
		client   = MongoClient(app.config['MONGO_HOST'])
		db       = client[klass.DATABASE]
		# return the relative mongodb collection
		collection = db[klass.__name__.lower()]
		return collection

	@classmethod
	def get(klass, limit=0, sort=None, **kwargs):
		criteria = {k:kwargs[k] for k in kwargs if kwargs[k] != None}
		cursor   = klass.collection.find(criteria, limit=limit)
		# sort
		if sort:
			if type(sort) in (list, tuple) and len(sort)==2:
				sort_id, sort_order = sort
			else:
				sort_id, sort_order = (sort, 1)
			cursor.sort(sort_id, sort_order)
		return cursor

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
			self.collection.insert(dict(attributes))

# -----------------------------------------------------------------------------
#
#    ARTICLE
#
# -----------------------------------------------------------------------------
class Article(Model):

	def __init__(self, **kwargs):
		self.title        = None
		self.date         = None
		self.content      = None
		self.summary      = None
		self.link         = None
		self.thematics    = None
		self.user         = None
		self.count_words  = None
		self.type         = None
		super(Article, self).__init__(**kwargs)

	def save(self):
		# count word
		if self.content and (not self.count_words or self.count_words == 0):
			self.count_words = len(self.content.split())
		# save
		super(Article, self).save()

	@classmethod
	def get(klass, limit=0, sort=("count_words", 1), **kwargs):
		return super(Article, klass).get(limit=limit, sort=sort, **kwargs)

	@classmethod
	def get_closest(klass, count_words, limit=1, silent=True, **kwargs):
		kwargs['sort'] = False
		# below
		kwargs['count_words'] = {"$lte": count_words}
		closest_below = list(klass.get(limit=limit, **kwargs).sort("count_words", -1))
		# above
		kwargs['count_words'] = {"$gt": count_words}
		closest_above = list(klass.get(limit=limit, **kwargs).sort("count_words", 1))
		results       = closest_above + closest_below
		# FIXME (old)
		# add delta parameter
		for i, result in enumerate(results):
			result['delta'] = abs(count_words - result['count_words'])
			if silent:
				del result['content']
		# sorting
		results = map(lambda args: klass(**args), results)
		results = sorted(results, key=lambda k: k.delta)
		return results[:limit]

# -----------------------------------------------------------------------------
#
#    USER
#
# -----------------------------------------------------------------------------
class User(Model):

	def __init__(self, **kwargs):
		self.username = None
		self.password = None
		self.email    = None
		super(User, self).__init__(**kwargs)

# -----------------------------------------------------------------------------
#
# TESTS
#
# -----------------------------------------------------------------------------
import unittest

class TestArticle(unittest.TestCase):

	def setUp(self):
		self.CustomArticle = Article
		self.CustomArticle.DATABASE = "timereader-dev"
		self.obj = self.CustomArticle()

	def tearDown(self):
		self.obj.collection.remove()

	def test_save(self):
		self.obj.content = "mot " * 3
		self.obj.save()
		assert self.obj.count_words
		assert type(self.obj.count_words)  is int
		assert type(self.obj.created_date) is datetime.datetime
		assert self.obj.count_words > 0

	def test_get(self):
		for i in range(10):
			a = self.CustomArticle(content="mot " * i)
			a.save()
		assert self.obj.get()[9]
		assert len(list(self.CustomArticle.get()))    == 10
		assert len(list(self.obj.get()))              == 10
		assert len(list(self.obj.get(limit=5)))       == 5
		assert len(list(self.obj.get(limit=0)))       == 10
		assert len(list(self.obj.get(count_words=5))) == 1

	def test_get_closest(self):
		for i in range(10):
			a = self.CustomArticle(content="mot " * i)
			a.save()
		assert len(self.CustomArticle.get_closest(5, limit=2))      == 2, self.CustomArticle.get_closest(5)
		assert self.CustomArticle.get_closest(5)[0].count_words     == 5
		assert self.CustomArticle.get_closest(5)[0].count_words     == 5
		assert self.CustomArticle.get_closest(10)[0].count_words    == 9
		assert self.CustomArticle.get_closest(0)[0].count_words     == 1

class TestUser(unittest.TestCase):

	def setUp(self):
		self.CustomUser          = User
		self.CustomUser.DATABASE = "timereader-dev"
		self.obj                 = self.CustomUser()

	def tearDown(self):
		self.obj.collection.remove()

	def test_save(self):
		self.obj.username = "<3"
		self.obj.password = "123"
		self.obj.email    = "aaa@bbb.com"
		self.obj.save()
		assert self.obj.username
		assert self.obj.password
		assert self.obj.email
		assert type(self.obj.created_date) is datetime.datetime

	def test_get(self):
		for i in range(10):
			a = self.CustomUser(username="mot " * i)
			a.save()
		assert len(list(self.CustomUser.get())) == 10

if __name__ == "__main__":
	unittest.main()

# EOF
