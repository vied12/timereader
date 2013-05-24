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
import os, json, uuid, pymongo, requests, datetime
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
@app.route('/api/coord/<keyword>')
def get_coord(keyword):
	# TODO
	res = requests.get("http://api.navitia.io/v0/paris/places.json?q={keyword}&type%5B%5D=stop_point&depth=0"\
		.format(keyword=keyword))
	data = res.json()
	return res.text
	# return "coord:2.3266505956562136:48.82738294324015"

@app.route('/api/stations/autocomplete/<keywords>', methods=['get'])
def station_autocomplete(keywords):
	# TODO
	return json.dumps([
		{
			"name": "Alésia",
			"uri": "coord:2.3266505956562136:48.82738294324015",
		},
		{
			"name": "Pouet pouet les bains",
			"uri": "coord:2.3266505956562136:48.82738294324015"
		},
		{
			"name": "Staligniouf",
			"uri": "coord:2.3266505956562136:48.82738294324015"
		}
	])

@app.route('/api/itineraire/<src>/<tgt>', methods=['get'])
def itineraire(src, tgt):
	response = {
		"origin"         : None,
		"destination"    : None,
		"begin_date_time": None,
		"end_date_time"  : None,
		"stations"       : [],
		"delta"          : None
	}
	# ensure we have coord uri
	if not src.startswith('coord:'):
		src = get_coord(src)
	if not tgt.startswith('coord:'):
		tgt = get_coord(tgt)
	# request nativia
	dt = datetime.datetime.now().strftime("%Y%m%dT%H%M")
	res = requests.get("http://api.navitia.io/v0/paris/journeys.json?origin={origin}&destination={destination}&datetime={datetime}&depth=0"\
		.format(origin=src, destination=tgt, datetime=dt))
	data = res.json()
	# fill response
	for journey in data['journeys']:
		for section in journey['sections']:
			if section['type'] == "PUBLIC_TRANSPORT":
				# TODO: check if Métro
				pp(section)
				# itineraire informations
				response["origin"]          = section['origin']['name']
				response["destination"]     = section['destination']['name']
				response["begin_date_time"] = section['begin_date_time']
				response["end_date_time"]   = section['end_date_time']
				response["delta"]           = (datetime.datetime.strptime(section['end_date_time'], '%Y%m%dT%H%M%f') - datetime.datetime.strptime(section['begin_date_time'], '%Y%m%dT%H%M%f')).total_seconds()
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
	return json.dumps(response)
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
