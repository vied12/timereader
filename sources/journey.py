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
import requests
import datetime

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

# EOF
