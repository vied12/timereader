# Encoding: utf-8
import os

DEBUG      = os.environ.get('DEBUG', False) == "True"
SECRET_KEY = os.environ.get('SECRET_KEY', "12345")

# -- AWS   -------------------------------
USE_S3                = True
AWS_ACCESS_KEY_ID     = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
S3_BUCKET_NAME        = os.environ.get('S3_BUCKET_NAME')
FLASK_ASSETS_USE_S3   = os.environ.get('FLASK_ASSETS_USE_S3', True)
ASSETS_DEBUG          = False
ASSETS_AUTO_BUILD     = False

# -- Queue -------------------------------
REDIS_URL        = os.environ['REDISTOGO_URL'] if 'REDISTOGO_URL' in os.environ else "redis://localhost:6379"
QUEUE_MODE_ASYNC = os.environ.get('QUEUE_MODE_ASYNC', False)

# -- Storage -----------------------------
if 'MONGOLAB_URI' in os.environ:
	MONGO_HOST = os.environ['MONGOLAB_URI']
	MONGO_DB   = os.environ['MONGOLAB_URI'].split('/')[-1]

# -- Source Content ----------------------
SOURCE_CONTENT = os.environ.get("SOURCE_CONTENT")

# -- Readabality -------------------------
READABILITY_CONSUMER_KEY     = os.environ.get("READABILITY_CONSUMER_KEY")
READABILITY_CONSUMER_SECRET  = os.environ.get("READABILITY_CONSUMER_SECRET")
READABILITY_PARSER_TOKEN     = os.environ.get("READABILITY_PARSER_TOKEN")

# -- QUE FAIRE À PARIS -------------------
QUEFAIREAPARIS_TOKEN = os.environ.get("QUEFAIREAPARIS_TOKEN")

# -- Twitter -----------------------------
TWITTER_CONSUMER_KEY             = os.environ.get("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET          = os.environ.get("TWITTER_CONSUMER_SECRET")
TWITTER_TEST_ACCESS_TOKEN        = os.environ.get("TWITTER_TEST_ACCESS_TOKEN")
TWITTER_TEST_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_TEST_ACCESS_TOKEN_SECRET")

# EOF
