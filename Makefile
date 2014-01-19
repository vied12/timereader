# Makefile -- TimeReader

WEBAPP     = $(wildcard webapp.py)

run:
	. `pwd`/.env ; python $(WEBAPP)

install:
	virtualenv venv --no-site-packages --distribute --prompt=TimeReader
	. `pwd`/.env ; pip install -r requirements.txt

# EOF
