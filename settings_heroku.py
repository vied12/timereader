# Encoding: utf-8
import os

DEBUG      = os.environ.get('DEBUG', False)
SECRET_KEY = os.environ.get('SECRET_KEY', "12345")

# -- Queue -------------------------------
REDIS_URL        = os.environ['REDISTOGO_URL'] if 'REDISTOGO_URL' in os.environ else "redis://localhost:6379"
QUEUE_MODE_ASYNC = os.environ.get('QUEUE_MODE_ASYNC', False)

# -- Storage -----------------------------
if 'MONGOLAB_URI' in os.environ:
	MONGO_HOST = os.environ['MONGOLAB_URI']
	MONGO_DB   = os.environ['MONGOLAB_URI'].split('/')[-1]
else:
	MONGO_HOST = 'localhost'
	MONGO_DB   = 'libreway'

# -- Source Content ----------------------
SOURCE_CONTENT = os.environ.get("SOURCE_CONTENT")

# -- Readabality -------------------------
READABILITY_CONSUMER_KEY     = os.environ.get("READABILITY_CONSUMER_KEY")
READABILITY_CONSUMER_SECRET  = os.environ.get("READABILITY_CONSUMER_SECRET")
READABILITY_PARSER_TOKEN     = os.environ.get("READABILITY_PARSER_TOKEN")

# -- QUE FAIRE À PARIS -------------------
API_QUEFAIREAPARIS_TOKEN = os.environ.get("API_QUEFAIREAPARIS_TOKEN")

# EOF
