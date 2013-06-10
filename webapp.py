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

from flask import Flask, render_template, request, send_file, render_template_string, \
	send_from_directory, Response, abort, session, redirect, url_for, make_response, jsonify
import os, json, uuid, pymongo, requests, datetime, bson, operator
from pymongo        import MongoClient
from bson.json_util import dumps
from werkzeug       import secure_filename
from base64         import b64decode
from pprint import pprint as pp
# import flask_s3
 
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
app.config.from_pyfile("settings.cfg")

def get_collection(collection):
	client = MongoClient(app.config['MONGO_HOST'])
	db     = client[app.config['MONGO_DB']]
	return db[collection]

def get_stations(name=None):
	stations = get_collection('stations')
	if not name:
		return stations.find()
	return stations.find({"name":{'$regex':"^%s" % name, "$options": "-i"}})

def get_closest(count_words, user=None, thema=None, limit=1):
	articles = get_collection('articles')
	words = count_words
	loc = {
		"user"       : user,
		"thematic"   : thema,
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
		# hack: remove content
		del result['content']
		results[i] = result
	# sorting
	results = sorted(results, key=lambda k: k['delta']) 
	return results[:limit]

def get_articles(user=None, thema=None, duration=None):
	articles = get_collection('articles')
	words    = (duration/60) * 300
	one      = get_closest(user=user, thema=thema, count_words=words, limit=3)
	two      = get_closest(user=user, thema=thema, count_words=words/2, limit=2)
	three    = get_closest(user=user, thema=thema, count_words=words/3, limit=3)
	return {
		"one"   : one,
		"two"   : two,
		"three" : three,
	}

def get_content(id):
	articles = get_collection('articles')
	return articles.find_one({"_id": bson.ObjectId(oid=str(id))})['content']

def get_referer():
	if 'referer' in session:
		referer = session['referer']
	else:
		referer = str(uuid.uuid4())
		session['referer'] = referer
	return referer

# -----------------------------------------------------------------------------
#
# API
#
# -----------------------------------------------------------------------------
@app.route('/api/stations/autocomplete/<keywords>', methods=['get'])
def station_autocomplete(keywords):
	# TODO
	res = []
	stations = get_stations(keywords)
	for station in stations:
		res.append({
			"name" : station['name'],
			"uri"  : "coord:%s:%s" % (station['lat'], station['lon'])
		})
	return json.dumps(res)

@app.route('/api/itineraire/<src>/<tgt>', methods=['get'])
def itineraire(src, tgt):
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
	# return res.text
	# on error
	if not data["response_type"] == "ITINERARY_FOUND":
		return res.text
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
					response["articles"]        = get_articles(duration=response["delta"])
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
	return dumps(response)

@app.route('/api/testarticles/')
def api_testarticles(user=None):
	articles = get_articles(duration=500)
	return dumps(articles)

@app.route('/api/content/<id>')
def api_content(id):
	content = get_content(id)
	return content

# -----------------------------------------------------------------------------
#
# Site pages
#
# -----------------------------------------------------------------------------
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/reset-content')
def reset_content():
	from content_maker import ContentMaker
	articles_collection = get_collection('articles')
	ContentMaker(articles_collection, "https://docs.google.com/spreadsheet/ccc?key=0AsZFwL3WjsakdFpOVGIwYS1iMlRHZGNkT0hvck9aeFE&usp=sharing&output=csv"
	articles_collection.remove()
	ContentMaker.start()
	return render_template('ok')


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
