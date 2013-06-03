#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : a Serious Toolkit
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# Author : Olivier Chardin                                <jegrandis@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 30-Jun-2012
# Last mod : 28-Aug-2012
# -----------------------------------------------------------------------------
import os, sys, subprocess, shpaml, clevercss, shutil

def preprocess(app, request):
	@app.before_request
	def render():
		if request.base_url.find("static") == -1:
			_collect_static(app)
			# _render_shpaml(app)
			# _render_coffee(app)
			# _render_coverCSS(app)
			# _render_jade(app)

def _scan(folder, dest, action, extension, new_extension=None):
	paths = []
	for path, subdirs, filenames in os.walk(folder):
		paths.extend([
			os.path.join(path, f)
			for f in filenames if os.path.splitext(f)[1] == extension
		])
	for path in paths:
		folder_char = '/'
		if os.name =='nt':
			folder_char='\\'
		directories   = path.split(folder_char)
		if 'lib' in directories:
			index_lib = directories.index('lib')
		else:
			index_lib = 0
		relative_path = folder_char.join(directories[0:index_lib+2])
		out = os.path.join(dest, os.path.splitext(os.path.relpath(path, relative_path))[0])
		if new_extension:
			out = "%s%s" % (out, new_extension)
		if not os.path.isfile(dest):
			dest_mtime = -1
		else:
			dest_mtime = os.path.getmtime(dest)
		f_mtime = os.path.getmtime(path)
		if f_mtime >= dest_mtime:
			action(path, out) 

def _render_coffee(app):	
	coffee_dir = os.path.join(app.config['LIB_DIR'], 'coffee')
	dest       = os.path.join(app.static_folder, "js")
	if os.name == 'nt':
		return None
	# delete previous file
	for path, subdirs, filenames in os.walk(coffee_dir):
		for coffee_file in filenames:
			coffee_name = os.path.splitext(coffee_file)[0]
			js_file     = os.path.join(dest, coffee_name+".js")
			if os.path.exists(js_file):
				os.remove(js_file)
	def action(source, dest):
		dest = os.path.dirname(dest)
		cmd  = 'coffee'
		if os.name == 'nt':
			cmd = 'coffee.cmd'
		subprocess.call([cmd, '-c', '--bare', '-o' ,  os.path.normcase(dest), source], shell=False)
	_scan(coffee_dir, dest, action, extension='.coffee', new_extension=".js")

def _render_jade(app):	
	jade_dir = os.path.join(app.config['LIB_DIR'], 'jade')
	dest     = os.path.join(app.root_path, app.template_folder)
	if not os.path.exists(dest):
		os.makedirs(dest)
	def action(source, dest):
		# dest= dest + ".html"
		cmd = 'pyjade'
		subprocess.call([cmd, '-c' , 'jinja' , '-o', dest, source], shell=False)
	_scan(jade_dir, dest, action, extension='.jade', new_extension=".html")


def _render_shpaml(app):
	shpaml_dir = os.path.join(app.config['LIB_DIR'], 'shpaml')
	dest       = os.path.join(app.root_path, app.template_folder)
	if not os.path.exists(dest):
		os.makedirs(dest)
	def action(source, dest):
		with open(source, 'r') as s:
			if not os.path.exists(os.path.dirname(dest)):
				os.makedirs(os.path.dirname(dest))
			with open(dest, 'w') as d:
				d.write(shpaml.convert_text(s.read()))
	_scan(shpaml_dir, dest, action, extension='.shpaml')

def _render_coverCSS(app):
	ccss_dir = os.path.join(app.config['LIB_DIR'], 'ccss')
	dest     = os.path.join(app.static_folder, "css")
	def action(source, dest):
		with open(source, 'r') as s:
			if not os.path.exists(os.path.dirname(dest)):
				os.makedirs(os.path.dirname(dest))
			with open(dest, 'w') as d:
				d.write(clevercss.convert(s.read()))
	_scan(ccss_dir, dest, action, extension='.ccss', new_extension='.css')

def _collect_static(app):
	static_dir = app.static_folder
	lib        = app.config['LIB_DIR']
	dir_to_collect = ['css', 'img', 'js', 'videos']
	for d in dir_to_collect:
		for path, subdirs, filenames in os.walk(os.path.join(lib, d)):
			for f in [os.path.join(path, filename) for filename in filenames]:
				if os.path.isfile(f):
					dst = os.path.join(static_dir, os.path.relpath(path, 'lib'), os.path.basename(f))
					if not os.path.exists(os.path.dirname(dst)):
						os.makedirs(os.path.dirname(dst))
					shutil.copyfile(f, dst)
	# _render_shpaml(app)
	_render_coffee(app)
	_render_coverCSS(app)
	# _render_jade(app)
# EOF
