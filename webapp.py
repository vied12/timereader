#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Time Reader
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 
# Last mod : 
# -----------------------------------------------------------------------------

from flask import Flask, render_template, request, send_file, render_template_string, \
	send_from_directory, Response, abort, session, redirect, url_for, make_response, jsonify
import os, json, uuid, requests, datetime, bson, operator

from bson.json_util import dumps
from werkzeug       import secure_filename
from base64         import b64decode
from pprint import pprint as pp
from storage import Station, Article
import readability
from worker import Worker
 
class CustomFlask(Flask):
	jinja_options = Flask.jinja_options.copy()
	jinja_options.update(dict(
		block_start_string    ='<%',
		block_end_string      ='%>',
		variable_start_string ='%%',
		variable_end_string   ='%%',
		comment_start_string  ='<#',
		comment_end_string    ='#>',
	))
 
app = CustomFlask(__name__)
app.config.from_envvar('TIMEREADER_SETTINGS')

worker = Worker(async=app.config['QUEUE_MODE_ASYNC'])

def get_referer():
	if 'referer' in session:
		referer = session['referer']
	else:
		referer = str(uuid.uuid4())
		session['referer'] = referer
	return referer

def how_many_words(duration):
	return (duration/60) * 300

def get_itineraire(src, tgt):
	response = {
		"origin"         : None,
		"destination"    : None,
		"begin_date_time": None,
		"end_date_time"  : None,
		"sections"       : [],
		"delta"          : None,
		"articles"       : []
	}

	dt = datetime.datetime.now().strftime("%Y%m%dT%H%M")
	res = requests.get("http://api.navitia.io/v0/paris/journeys.json?origin={origin}&destination={destination}&datetime={datetime}&depth=0"\
		.format(origin=src, destination=tgt, datetime=dt))
	data = res.json()
	# on error
	if not data["response_type"] == "ITINERARY_FOUND":
		raise Exception(res.text)
	# fill response
	for journey in data['journeys']:
		for section in journey['sections']:
			if section['type'] == "PUBLIC_TRANSPORT" and section['pt_display_informations']['physical_mode'] == "Metro":
				# we found a journeys which contains a metro section
				# we save the global informations about travel ONCE
				if not response['origin']:
					response['origin'] = section['origin']['name']
					# destination will be filled later
					response["delta"]           = journey['duration']
					response["begin_date_time"] = section['begin_date_time']
					response["end_date_time"]   = section['end_date_time']
				# we save all sections
				stations = []
				for station in section['stop_date_times']:
					if len(stations) > 0:
						delta = datetime.datetime.strptime(station['departure_date_time'], '%Y%m%dT%H%M%f') - datetime.datetime.strptime(stations[-1]['arrival_date_time'], '%Y%m%dT%H%M%f')
						delta = delta.total_seconds()
					elif response['sections']:
						# delta of correspondance
						delta = datetime.datetime.strptime(station['departure_date_time'], '%Y%m%dT%H%M%f') - datetime.datetime.strptime(response['sections'][-1]['stations'][-1]['arrival_date_time'], '%Y%m%dT%H%M%f')
						delta = delta.total_seconds()
					else:
						delta = 0
					stations.append({
						"name"                : station['stop_point']['name'],
						"departure_date_time" : station['departure_date_time'],
						"arrival_date_time"   : station['arrival_date_time'],
						"timedelta"           : delta
					})
				response['sections'].append({
					"stations" : stations,
					"line"     : section['pt_display_informations']['code'],
					"color"    : "#"+section['pt_display_informations']['color'],
					"origin"          : section['origin']['name'],
					"destination"     : section['destination']['name'],
					"begin_date_time" : section['begin_date_time'],
					"end_date_time"   : section['end_date_time'],
				})
				response['destination'] = section['destination']['name']
		if response['origin']:
			break
	return response

# -----------------------------------------------------------------------------
#
# API
#
# -----------------------------------------------------------------------------
@app.route('/api/stations/autocomplete/<keywords>', methods=['get'])
def station_autocomplete(keywords):
	# TODO
	res = []
	stations = Station.get(keywords)
	for station in stations:
		res.append({
			"name" : station['name'],
			"uri"  : "coord:%s:%s" % (station['lat'], station['lon'])
		})
	return json.dumps(res)

@app.route('/api/itineraire/<src>/<tgt>', methods=['get'])
@app.route('/api/itineraire/<src>/<tgt>/thematics/<thematics>', methods=['get'])
@app.route('/api/itineraire/<src>/<tgt>/user/<user_id>', methods=['get'])
def get_content_from_itineraire(src, tgt, thematics=None, user_id=None):
	itineraire = get_itineraire(src, tgt)
	duration   = itineraire['delta']
	words      = how_many_words(duration)
	thematics  = thematics.split(',') if thematics else None
	articles   = {
		"one"   : Article.get_closest(count_words=words,   limit=3, thematics=thematics, user=user_id), # FIXME
		"two"   : Article.get_closest(count_words=words/2, limit=2, thematics=thematics, user=user_id),
		"three" : Article.get_closest(count_words=words/3, limit=3, thematics=thematics, user=user_id),
	}
	itineraire["articles"] = articles
	return dumps(itineraire)

@app.route('/api/duration/<duration>', methods=['get'])
@app.route('/api/duration/<duration>/thematics/<thematics>', methods=['get'])
@app.route('/api/duration/<duration>/user/<user_id>', methods=['get'])
def get_content_from_duration(duration, thematics=None, user_id=None):
	words      = how_many_words(int(duration))
	thematics  = thematics.split(',') if thematics else None
	articles   = {
		"one"   : Article.get_closest(count_words=words,   limit=3, thematics=thematics, user=user_id), # FIXME
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
	return render_template('index.html')

# FIXME: needs authentication
@app.route('/reset-content')
def reset_content():
	from content_maker import ContentMaker
	articles_collection = Article.get_collection()
	articles_collection.remove()
	worker.run('retrieve_common_articles', app.config['SOURCE_CONTENT'])
	return "ok"

# -----------------------------------------------------------------------------
#
# Utils
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
		app.run(host='0.0.0.0')
# EOF
