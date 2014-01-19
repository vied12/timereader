# Makefile -- TimeReader

WEBAPP     = $(wildcard **/webapp.py)
ENV        = `pwd`/.env

run:
	mongod &
	. $(ENV) ; python $(WEBAPP)

install:
	virtualenv venv --no-site-packages --distribute --prompt=TimeReader
	. $(ENV) ; pip install -r requirements.txt

clear:
	rm -rf webapp/static/.webassets-cache
	rm -rf webapp/static/gen

# EOF
