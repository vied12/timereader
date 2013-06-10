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
	This script scape a google calc which contains source,
		and feed the database with the source's content 
"""

from pymongo import MongoClient
from flask import Flask
from pprint import pprint as pp
from content_maker import ContentMaker

if __name__ == "__main__":

	app = Flask(__name__)
	app.config.from_pyfile("../settings.cfg")

	client     = MongoClient(app.config['MONGO_HOST'])
	db         = client[app.config['MONGO_DB']]
	collection =  db["articles"]

	# FIXME: remove it
	collection.remove()

	content_maker = ContentMaker(collection, "https://docs.google.com/spreadsheet/ccc?key=0AsZFwL3WjsakdFpOVGIwYS1iMlRHZGNkT0hvck9aeFE&usp=sharing&output=csv")

	content_maker.start()

# EOF