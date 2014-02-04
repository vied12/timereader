#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Time Reader
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 23-May-2013
# Last mod : 19-Jan-2014
# -----------------------------------------------------------------------------

from bson.json_util   import dumps
from storage          import Station, Article
from worker           import Worker
from flask.ext.assets import Environment, YAMLLoader
import journey
import readability
import json
import uuid
import os
import flask
import utils

PWD = os.path.dirname(os.path.abspath(__file__))

# create an instance of flask with a custom config (different template tags)
app = utils.CustomFlask(__name__)
# load config file
app.config.from_envvar('TIMEREADER_SETTINGS')

# process assets
assets  = Environment(app)
bundles = YAMLLoader(os.path.join(PWD, "assets.yaml")).load_bundles()
assets.register(bundles)

#s3
from flask_s3 import FlaskS3
s3 = FlaskS3(app)

# create a job queue
worker = Worker(async=app.config['QUEUE_MODE_ASYNC'])

# -----------------------------------------------------------------------------
#
# API
#
# -----------------------------------------------------------------------------
@app.route('/api/stations/autocomplete/<keywords>', methods=['get'])
def station_autocomplete(keywords):
	res = []
	stations = Station.get(keywords)
	for station in stations:
		res.append({
			"name" : station['name'],
			"uri"  : "coord:%s:%s" % (station['lon'], station['lat'])
		})
	return json.dumps(res)

@app.route('/api/itineraire/<src>/<tgt>', methods=['get'])
@app.route('/api/itineraire/<src>/<tgt>/thematics/<thematics>', methods=['get'])
@app.route('/api/itineraire/<src>/<tgt>/user/<user_id>', methods=['get'])
@app.route('/api/itineraire/<src>/<tgt>/thematics/<thematics>/user/<user_id>', methods=['get'])
def get_content_from_itineraire(src, tgt, thematics=None, user_id=None):
	itineraire = journey.get_itineraire(src, tgt)
	duration   = itineraire['delta']
	words      = utils.how_many_words(duration)
	thematics  = thematics.split(',') if thematics else None
	articles   = {
		"one"   : Article.get_closest(count_words=words,   limit=5, thematics=thematics, user=user_id), # FIXME
		"two"   : Article.get_closest(count_words=words/2, limit=2, thematics=thematics, user=user_id),
		"three" : Article.get_closest(count_words=words/3, limit=3, thematics=thematics, user=user_id),
	}
	itineraire["articles"] = articles
	return dumps(itineraire)

@app.route('/api/duration/<duration>', methods=['get'])
@app.route('/api/duration/<duration>/thematics/<thematics>', methods=['get'])
@app.route('/api/duration/<duration>/user/<user_id>', methods=['get'])
@app.route('/api/duration/<duration>/thematics/<thematics>/user/<user_id>', methods=['get'])
def get_content_from_duration(duration, thematics=None, user_id=None):
	words      = utils.how_many_words(int(duration))
	thematics  = thematics.split(',') if thematics else None
	articles   = {
		"one"   : Article.get_closest(count_words=words,   limit=5, thematics=thematics, user=user_id), # FIXME
		"two"   : Article.get_closest(count_words=words/2, limit=2, thematics=thematics, user=user_id),
		"three" : Article.get_closest(count_words=words/3, limit=3, thematics=thematics, user=user_id),
	}
	return dumps({'articles': articles, 'delta': duration})

@app.route('/api/content/<id>')
def api_content(id):
	article  = Article.get(id=id)
	if article:
		return article['content']
	return "false"


@app.route('/api/readability/<username>/<password>', methods=['get'])
def api_readability_register(username, password):
	token = readability.xauth(
		app.config['READABILITY_CONSUMER_KEY'], 
		app.config['READABILITY_CONSUMER_SECRET'], 
		username,
		password)
	# oauth_token, oauth_secret = token
	# FIXME: should be in SESSION
	user_id = str(uuid.uuid4())
	# Retrieve the user's articles and save them into the database with his user_id
	worker.run('retrieve_readability', token, user_id)
	return dumps({'user': user_id})

# -----------------------------------------------------------------------------
#
# Site pages
#
# -----------------------------------------------------------------------------
@app.route('/')
def index():
	return flask.render_template('index.html')

@app.route('/all-articles')
def all_articles():
	return flask.render_template('index.html',articles=Article.get_collection().find())

# FIXME: needs authentication
@app.route('/reset-content')
def reset_content():
	articles_collection = Article.get_collection()
	articles_collection.remove()
	worker.run('retrieve_common_articles', app.config['SOURCE_CONTENT'])
	return "ok"

# -----------------------------------------------------------------------------
#
# Triggers
#
# -----------------------------------------------------------------------------
@app.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	return response

# -----------------------------------------------------------------------------
#
# Main
#
# -----------------------------------------------------------------------------
if __name__ == '__main__':
	app.run(host='0.0.0.0', extra_files=(os.path.join(PWD, "assets.yaml"),))

# EOF
