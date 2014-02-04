#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Time Reader
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 09-Jul-2013
# Last mod : 09-Jul-2013
# -----------------------------------------------------------------------------
from . import Job, job
from storage import Article
from flask import Flask
import requests
import datetime

app = Flask(__name__)
app.config.from_envvar('TIMEREADER_SETTINGS')

@job("RetrieveQuefaireaparis")
class RetrieveQuefaireaparis(Job):

	def run(self):
		response = requests.get("https://api.paris.fr:3000/data/1.1/QueFaire/get_activities/?token={token}&created={created}&offset={offset}&limit={limit}"
			.format(
				token   = app.config['API_QUEFAIREAPARIS_TOKEN'],
				created = "0",
				offset  = "0",
				limit   = "100"),
			verify=False
		)
		results = response.json()
		for result in results['data']:
			article = Article()
			article.title       = result['nom']
			article.date        = datetime.datetime.strptime(result['created'], '%Y-%m-%dT%H:%M:%S.%fZ')
			article.content     = result['description']
			article.summary     = result['small_description']
			article.thematic    = "quefaireaparis" # FIXME
			article.type        = "quefaireaparis"
			# special fields
			article.occurences  = result['occurences']
			article.thematics   = [_['rubrique'] for _ in result['rubriques']]
			article.location    = dict(lat=result['lat'], lon=result['lon'])
			article.save()

# EOF
