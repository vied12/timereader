#!/usr/bin/env python
# Encoding: utf-8
from pymongo import MongoClient
from flask import Flask
from pprint import pprint as pp
import sys
import json
import feedparser
import requests

# Techno, internat, life style, culture, sport,  news

FLUX = [
	# {"thematic":"life-style",    "name": "Le Monde", "url":'http://www.lemonde.fr/rss/tag/ete.xml'}, # été
	# {"thematic":"international", "name": "Le Monde", "url":'http://rss.lemonde.fr/c/205/f/3052/index.rss'}, # internat
	# {"thematic":"news",          "name": "Le Monde", "url":'http://rss.lemonde.fr/c/205/f/3067/index.rss'}, # politique
	# {"thematic":"sport",         "name": "Le Monde", "url":'http://rss.lemonde.fr/c/205/f/3058/index.rss'},
	# {"thematic":"culture",       "name": "Le Monde", "url":'http://rss.lemonde.fr/c/205/f/3060/index.rss'},
	# {"thematic":"thechno",       "name": "Le Monde", "url":'http://www.lemonde.fr/rss/tag/sciences.xml'}, # science
	# {"thematic":"culture",       "name": "Le Monde", "url":'http://www.lemonde.fr/rss/tag/style.xml'}, # style
	{"thematic": "techno", "name":"planet Ubuntu", "url": 'http://www.planet-libre.org/feed.php?type=rss'},
]

app = Flask(__name__)
app.config.from_pyfile("../settings.cfg")

client     = MongoClient(app.config['MONGO_HOST'])
db         = client[app.config['MONGO_DB']]
collection =  db["articles"]

collection.remove()

for flux in FLUX:

	d = feedparser.parse(flux['url'])

	for article in d['entries']:
		link = article['link'].split('#')
		if len(link) > 1:
			link = "".join(link[0:-1])
		else:
			link = link[0]

		content = article['content'][0]['value']
		# if link:
		# 	r = requests.get("http://boilerpipe-web.appspot.com/extract?url={url}&extractor=ArticleExtractor&output=htmlFragment&extractImages="\
		# 		.format(url=link))
		# 	content = r.text
		# 	content = content.replace('\n', '')
			# content = content.encode('utf8')
			# content = content.encode('ascii')
			# content = r.text.encode(encoding='UTF-8',errors='strict')
			# content = r.text.translate(dict.fromkeys(range(32)))
		# else:
		# 	content = article['summary']
		res  = {
			"title"    : article['title'],
			"content"  : content,
			"summary"  : article['summary'],
			"link"     : link,
			"source"   : flux['name'],
			"thematic" : flux['thematic']
		}
		collection.insert(res)

# EOF
