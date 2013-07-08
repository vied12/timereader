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
from job import Job
from storage import Article
from flask import Flask
import requests
from worker import Worker

app = Flask(__name__)
app.config.from_envvar('TIMEREADER_SETTINGS')
worker = Worker(async=False)

class RetrieveQuefaireaparis(Job):

	def run(self):
		response = requests.get("https://api.paris.fr:3000/data/1.1/QueFaire/get_activities/?token={token}&created={created}&offset={offset}&limit={limit}"
			.format(
				token   = "",
				created = "0",
				offset  = "0",
				limit   = "1000")
		)
		print response.text

# EOF