#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Time Reader
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 06-Jul-2013
# Last mod : 03-Feb-2014
# -----------------------------------------------------------------------------
import importlib

class Job(object):

	def run(self, *args, **kwargs):
		raise Exception('needs to be implemented')

# -----------------------------------------------------------------------------
#
# CATALOGUE
#
# -----------------------------------------------------------------------------
class Catalogue:
	"""The Catalogue is a singleton that acts a registry for jobs"""

	JOBS    = {}

	@classmethod
	def RegisterJob( self, name, description, job_class ):
		if name in self.JOBS: return job_class
		self.JOBS[name] = {
			"name"  :name,
			"doc"   :description,
			"class" :job_class
		}
		return job_class

# -----------------------------------------------------------------------------
#
# DECORATORS
#
# -----------------------------------------------------------------------------
def job(description):
	"""A decorator that allows to declare a specific job with its
	documentation."""
	def wrapper(_):
		return Catalogue.RegisterJob( _.__module__.split('.')[-1], description, _ )
	return wrapper

def perform_jobs_import(val):
	importlib.import_module(val)
	module_name = val.split('.')[-1]
	return Catalogue.JOBS[module_name]['class']

# EOF
