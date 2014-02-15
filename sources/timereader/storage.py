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

import itertools
class Cursor(object):
	def __init__(self, cursor, model):
		self.cursor = cursor
		self.model  = model
	def __iter__(self):
		for elt in self.cursor:
			yield self.model(**elt)
	def __getitem__(self,index):
		try:
			return self.model(**next(itertools.islice(self.cursor,index,index+1)))
		except TypeError:
			return list(itertools.islice(self.cursor,index.start,index.stop,index.step))

class Storable(object):
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
	def _get(klass, limit=0, sort=None, **kwargs):
		criteria = {k:kwargs[k] for k in kwargs if kwargs[k] != None}
		cursor   = klass.collection.find(criteria, limit=limit)
		# sort
		if sort:
			if type(sort) in (list, tuple) and len(sort)==2:
				sort_id, sort_order = sort
			else:
				sort_id, sort_order = (sort, 1)
			response = cursor.sort(sort_id, sort_order)
		return cursor

	@classmethod
	def get(klass, limit=0, sort=None, **kwargs):
		return Cursor(klass._get(limit, sort, **kwargs), klass)

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

	def __str__(self):
		return super(Model, self).__str__().replace(self.__class__.__name__, "Storage%s" % (self.__class__.__name__))

# EOF
