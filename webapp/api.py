#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Time Reader
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 27-Feb-2014
# Last mod : 27-Feb-2014
# -----------------------------------------------------------------------------
from flask.ext.restful import Resource, fields, marshal, reqparse
from timereader import Article, User
from bson.objectid import ObjectId

article_fields = {
	'title'       : fields.String,
	'content'     : fields.String,
	'created_date': fields.DateTime,
	'summary'     : fields.String,
	'link'        : fields.String,
	'origin'      : fields.String,
}

class ArticlesResource(Resource):

	def get(self):
		return [marshal(a, article_fields) for a in Article.get()[:10]]

	def post(self):
		pass
	
class ArticleResource(Resource):

	def get(self, article_id):
		article = Article.get_one({"_id":ObjectId(article_id)})
		return marshal(article.__dict__, article_fields)

	def put(self, article_id):
		pass

	def delete(self, article_id):
		pass

user_fields = {
	'username'       : fields.String,
	'languages'      : fields.String,
	'main_language'  : fields.Raw,
}

class UsersResource(Resource):

	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('username', type=str, required=True)
		parser.add_argument('password', type=str, required=True)
		# TODO: check email
		parser.add_argument('email', type=str, required=True)
		args = parser.parse_args()
		user = User(**args)
		user.save()
		return args

class UserResource(Resource):

	def get(self, username):
		user = User.get_one({"username":username})
		return marshal(user.__dict__, user_fields)

	def put(self, username):
		pass

	def delete(self, username):
		pass

# EOF
