#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Time Reader
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 03-Feb-2014
# Last mod : 03-Feb-2014
# -----------------------------------------------------------------------------
from . import Job
from worker import Worker
from flask import Flask

app = Flask(__name__)
app.config.from_envvar('TIMEREADER_SETTINGS')
worker = Worker(async=False)

class RetrieveTwitter(Job):
	pass

# EOF
