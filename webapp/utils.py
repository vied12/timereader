#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Time Reader
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 19-Jan-2014
# Last mod : 19-Jan-2014
# -----------------------------------------------------------------------------
from flask import Flask

class CustomFlask(Flask):
	jinja_options = Flask.jinja_options.copy()
	jinja_options.update(dict(
		block_start_string    ='[%',
		block_end_string      ='%]',
		variable_start_string ='[[',
		variable_end_string   =']]',
		comment_start_string  ='[#',
		comment_end_string    ='#]',
))

def how_many_words(duration):
	return (duration/60) * 300

# EOF
