#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : 
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 
# Last mod : 
# -----------------------------------------------------------------------------

from flask import Flask, render_template, request, send_file, \
	send_from_directory, Response, abort, session, redirect, url_for, make_response
import os, json, uuid, pymongo
from pymongo        import MongoClient
from bson.json_util import dumps
# from httplib2       import Http
from werkzeug       import secure_filename
from base64         import b64decode
# import flask_s3

app       = Flask(__name__)
app.config.from_pyfile("settings.cfg")

# -----------------------------------------------------------------------------
#
# API
#
# -----------------------------------------------------------------------------
@app.route('/api/', methods=['get'])
def test_api():
	return "coucou"

# -----------------------------------------------------------------------------
#
# Site pages
#
# -----------------------------------------------------------------------------

@app.route('/')
def index():
	return render_template('home.html')

# -----------------------------------------------------------------------------
#
# Utils
#
# -----------------------------------------------------------------------------
# @app.route('/uploaded/<filename>')
# def uploaded_file(filename):
# 	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
# -----------------------------------------------------------------------------
#
# Main
#
# -----------------------------------------------------------------------------

if __name__ == '__main__':
	import preprocessing.preprocessing as preprocessing
	import sys
	if len(sys.argv) > 1 and sys.argv[1] == "collectstatic":
		preprocessing._collect_static(app)
		if 'USE_S3' in app.config:
			flask_s3.create_all(app)
	else:
		# render ccss, coffeescript and shpaml in 'templates' and 'static' dirs
		preprocessing.preprocess(app, request) 
		# set FileSystemCache instead of Memcache for development
		# cache = werkzeug.contrib.cache.FileSystemCache(os.path.join(app.root_path, "cache"))
		# run application
		app.run()
# EOF
