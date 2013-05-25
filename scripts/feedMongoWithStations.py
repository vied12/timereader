#!/usr/bin/env python
# Encoding: utf-8
import json
from pymongo import MongoClient
from flask import Flask
app = Flask(__name__)
app.config.from_pyfile("../settings.cfg")

with open("data/stations.csv") as f:
	pouet = []
	# stop_id,stop_code,stop_name,stop_desc,latitude,longitude,location_type,parent_station
	for line in f.readlines()[1:]:
		data = line.split('#')
		res = {
		# "stop_id":data[0],
		"lat":data[1],
		"lon":data[2],
		"name":data[3],
		"description":data[4],
		"type":data[5].strip("\r\n"),
		}
		pouet.append(res)

client = MongoClient(app.config['MONGO_HOST'])
db     = client[app.config['MONGO_DB']]
collection =  db["stations"]
for sta in pouet:
	collection.insert(sta)
