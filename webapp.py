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
	send_from_directory, Response, abort, session, redirect, url_for, make_response, jsonify
import os, json, uuid, pymongo, requests, datetime, bson, operator
from pymongo        import MongoClient
from bson.json_util import dumps
from werkzeug       import secure_filename
from base64         import b64decode
from pprint import pprint as pp
# import flask_s3

app       = Flask(__name__)
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
	print "bla"
	articles = get_collection('articles')
	words    = (duration/60) * 300
	one      = get_closest(user=user, thema=thema, count_words=words)
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
		"stations"       : [],
		"line"           : None,
		"color"          : None,
		"delta"          : None,
		"articles"       : []
	}
	# ensure we have coord uri
	# if not src.startswith('coord:'):
	# 	src = get_coord(src)
	# if not tgt.startswith('coord:'):
	# 	tgt = get_coord(tgt)
	# request nativia
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
				# itineraire informations
				response["origin"]          = section['origin']['name']
				response["destination"]     = section['destination']['name']
				response["begin_date_time"] = section['begin_date_time']
				response["end_date_time"]   = section['end_date_time']
				response["line"]            = section['pt_display_informations']['code']
				response["color"]           = "#"+section['pt_display_informations']['color']
				response["delta"]           = (datetime.datetime.strptime(section['end_date_time'], '%Y%m%dT%H%M%f') - datetime.datetime.strptime(section['begin_date_time'], '%Y%m%dT%H%M%f')).total_seconds()
				response["articles"]        = get_articles(duration=response["delta"])
				# stations
				for station in section['stop_date_times']:
					if len(response['stations']) > 0:
						delta = datetime.datetime.strptime(station['departure_date_time'], '%Y%m%dT%H%M%f') - datetime.datetime.strptime(response['stations'][-1]['arrival_date_time'], '%Y%m%dT%H%M%f')
						delta = delta.total_seconds()
					else:
						delta = 0
					response['stations'].append({
						"name"                : station['stop_point']['name'],
						"departure_date_time" : station['departure_date_time'],
						"arrival_date_time"   : station['arrival_date_time'],
						"timedelta"           : delta
					})
	return dumps(response)

# @app.route('/api/articles/')
# def api_articles(user=None):
# 	articles = get_articles(duration=200)
# 	return dumps(articles)
	# text= r'''[{"thematic": "life-style", "title": "A Perpignan, l'Afrique prend la parole", "summary": "Filda Adoch, Ougandaise, commente les images de Martina Bacigalupo et sort des clich\u00e9s.", "content": "Filda Adoch, Ougandaise, commente les images de Martina Bacigalupo et sort des clich\u00e9s.", "source": "http://www.lemonde.fr/rss/tag/ete.xml", "link": "", "_id": {"$oid": "51a077eb3062721886fafe33"}}, {"thematic": "life-style", "title": "Li Chengpeng, le sport sans tabou en Chine", "summary": "Ancien commentateur sportif, Li Chengpeng a choisi de se consacrer \u00e0 l'\u00e9criture apr\u00e8s avoir re\u00e7u des menaces de mort. Par le biais de son blog, mais aussi de fictions, il aborde sans fard les sujets qui d\u00e9rangent.", "content": "Ancien commentateur sportif, Li Chengpeng a choisi de se consacrer \u00e0 l'\u00e9criture apr\u00e8s avoir re\u00e7u des menaces de mort. Par le biais de son blog, mais aussi de fictions, il aborde sans fard les sujets qui d\u00e9rangent.", "source": "http://www.lemonde.fr/rss/tag/ete.xml", "link": "", "_id": {"$oid": "51a077eb3062721886fafe34"}}, {"thematic": "life-style", "title": "Christian Portal, soigner par les plantes", "summary": "D\u00e9non\u00e7ant une d\u00e9marche de soin\u00a0\"tourn\u00e9e essentiellement sur l'augmentation des profits\", Christian Portal plaide, \u00e0 travers son blog, pour une m\u00e9decine \u00e9cologique.", "content": "D\u00e9non\u00e7ant une d\u00e9marche de soin\u00a0\"tourn\u00e9e essentiellement sur l'augmentation des profits\", Christian Portal plaide, \u00e0 travers son blog, pour une m\u00e9decine \u00e9cologique.", "source": "http://www.lemonde.fr/rss/tag/ete.xml", "link": "", "_id": {"$oid": "51a077eb3062721886fafe35"}}, {"thematic": "life-style", "title": "Anne Lataillade, du beau et du bon au menu", "summary": "Fuyant les plats compliqu\u00e9s, Anne Lataillade propose, via son blog, \"Papilles et pupilles\", des recettes inspir\u00e9es par une cuisine familiale, \u00e0 la port\u00e9e de tous.", "content": "Fuyant les plats compliqu\u00e9s, Anne Lataillade propose, via son blog, \"Papilles et pupilles\", des recettes inspir\u00e9es par une cuisine familiale, \u00e0 la port\u00e9e de tous.", "source": "http://www.lemonde.fr/rss/tag/ete.xml", "link": "", "_id": {"$oid": "51a077eb3062721886fafe36"}}, {"thematic": "life-style", "title": "\"La prestesse du mal est inou\u00efe\"", "summary": "", "content": "", "source": "http://www.lemonde.fr/rss/tag/ete.xml", "link": "", "_id": {"$oid": "51a077eb3062721886fafe37"}}]'''
	# return Response(response=text,
	# 	status=200,
	# 	mimetype="application/json")

@app.route('/api/testarticles/')
def api_testarticles(user=None):
	articles = get_articles(duration=200)
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
	return render_template('home.html')

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
