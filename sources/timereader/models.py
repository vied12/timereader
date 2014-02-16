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
# Last mod : 16-Feb-2014
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
		self.origin       = None
		self.META         = dict(
			words_count   = None,
			complexity    = None,
			type          = None,
			tags          = None,
			sources       = None,
		)
		super(Article, self).__init__(**kwargs)

	def save(self):
		# count word
		if self.content and (not self.META["words_count"] or self.META["words_count"] == 0):
			self.META["words_count"] = len(self.content.split())
		# save
		super(Article, self).save()

	@classmethod
	def get(klass, query={}, limit=0, sort=("META.words_count", 1), **kwargs):
		return super(Article, klass).get(query=query, limit=limit, sort=sort, **kwargs)

	@classmethod
	def get_closest(klass, words_count, limit=1, **kwargs):
		kwargs['sort'] = False
		# below
		kwargs['META.words_count'] = {"$lte": words_count}
		closest_below = list(klass._get(limit=limit, **kwargs).sort("META.words_count", -1))
		# above
		kwargs['META.words_count'] = {"$gt": words_count}
		closest_above = list(klass._get(limit=limit, **kwargs).sort("META.words_count", 1))
		results       = closest_above + closest_below
		# FIXME (old)
		# add delta parameter
		for result in results:
			result['META']['delta'] = abs(words_count - result["META"]["words_count"])
			# if silent:
			# 	del result['content']
		# sorting
		results = map(lambda args: klass(**args), results)
		results = sorted(results, key=lambda k: k.META.get("delta"))
		return results[:limit]

# -----------------------------------------------------------------------------
#
#    USER
#
# -----------------------------------------------------------------------------
class User(Storable):

	def __init__(self, **kwargs):
		self.username      = None
		self.password      = None
		self.email         = None
		self.languages     = {}
		self.main_language = None
		self.articles      = []

		super(User, self).__init__(**kwargs)

	def validate(self):
		assert self.email
		assert self.password
		assert self.username
		assert not self.main_language or self.main_language in self.languages.keys()

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
		assert self.obj.META["words_count"]
		assert type(self.obj.META["words_count"])  is int
		assert type(self.obj.created_date) is datetime.datetime
		assert self.obj.META["words_count"] > 0
		self.assertIsNotNone(self.obj._id)
		self.assertIsNotNone(self.obj['_id'])

	def test_get(self):
		for i in range(10):
			a = self.CustomArticle(content="mot " * i)
			a.save()
		assert self.obj.get()[9]
		self.assertEqual(len(list(self.CustomArticle.get()))    , 10)
		self.assertEqual(len(list(self.obj.get()))              , 10)
		self.assertEqual(len(list(self.obj.get(limit=5)))       , 5)
		self.assertEqual(len(list(self.obj.get(limit=0)))       , 10)
		self.assertEqual(len(list(self.obj.get({"META.words_count":5}))) , 1)
		for e in self.obj.get():
			self.assertEqual(type(e), Article)

	def test_get_closest(self):
		for i in range(10):
			a = self.CustomArticle(content="mot " * i)
			a.save()
		self.assertEqual(len(self.CustomArticle.get_closest(5, limit=2))          , 2)
		self.assertEqual(self.CustomArticle.get_closest(5)[0].META["words_count"] , 5)
		self.assertEqual(self.CustomArticle.get_closest(10)[0].META["words_count"], 9)
		self.assertEqual(self.CustomArticle.get_closest(0)[0].META["words_count"] , 1)

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
		self.assertIsNotNone(self.obj.username)
		self.assertIsNotNone(self.obj.password)
		self.assertIsNotNone(self.obj.email)
		self.assertIsNotNone(self.obj._id)
		self.assertEqual(type(self.obj.created_date), datetime.datetime)
		self.obj.email = "pouet"
		self.obj.save()
		self.assertIsNotNone(self.obj._id)
		self.assertEqual(self.obj.email, "pouet")
		# test validation
		user = self.CustomUser(username="coucou")
		self.assertRaises(AssertionError, user.save)

	def test_get(self):
		for i in range(10):
			a = self.CustomUser(username="name%s" % i, password="1234", email="ddd@ff.com")
			a.save()
		self.assertEqual(len(list(self.CustomUser.get())), 10)

	def test_get_one(self):
		for i in range(10):
			a = self.CustomUser(username="name%s" % i, password="1234", email="ddd@ff.com")
			a.save()
		user = self.CustomUser.get_one({"username" : "name1"})
		self.assertEqual(type(user), User)
		user = self.CustomUser.get_one({"username" : "unknown"})
		self.assertIsNone(user)

if __name__ == "__main__":
	unittest.main()

# EOF
