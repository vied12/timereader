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
# Last mod : 15-Feb-2014
# -----------------------------------------------------------------------------
from storage import Storable
import unittest
import datetime
# -----------------------------------------------------------------------------
#
#    ARTICLE
#
# -----------------------------------------------------------------------------

class Article(Storable):

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
		closest_below = list(klass._get(limit=limit, **kwargs).sort("count_words", -1))
		# above
		kwargs['count_words'] = {"$gt": count_words}
		closest_above = list(klass._get(limit=limit, **kwargs).sort("count_words", 1))
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
class User(Storable):

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
		for e in self.obj.get():
			assert type(e) is Article

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
