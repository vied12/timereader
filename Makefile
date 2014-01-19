# Makefile -- TimeReader

WEBAPP     = $(wildcard **/webapp.py)

run:
	mongod &
	. `pwd`/.env ; python $(WEBAPP)

install:
	virtualenv venv --no-site-packages --distribute --prompt=TimeReader
	. `pwd`/.env ; pip install -r requirements.txt

clear:
	rm -rf webapp/static/.webassets-cache
	rm -rf webapp/static/gen

# EOF

