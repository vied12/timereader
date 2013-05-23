Libreway
========

A reading companion for traveling by subway. 

Paris 2013 - Developed during the Open-data Hackathon for RATP. 


## Pitch
todo

## The application

This application run with:
* Python 2.7
* Flask 0.9
* Mongodb
* CoffeeScript
* CleverCSS
* PyJade (with the jinja2 templating engine)

## Installation

### Dependances

First, you need to install dependances. We will use `pip` to do that.

Tips: Prefere to use `virtualenv` to isolate application dependances from your system.

Now, how to do that with debian|ubuntu:

Install pip and basic dependances (gcc, python lib) to build others dependances

	$ sudo apt-get install build-essential python-pip python-dev

Install virtualenv

	$ sudo pip install virtualenv

Create a virtualenv

	$ virtualenv --no-site-packages --distribute venv

Add the virtualenv to your python path with
	
	$ source .env

Download and install python dependances

	$ virtualenv install -r requirements.txt

#### No Python dependances

* [Mongodb](http://www.mongodb.org/)
* [CoffeeScript](http://coffeescript.org/)

### Launch

Add the virtualenv to your python path with:
	
	$ source .env

Generate all static files:

	$ ./webapp collectstatic

Tips: use [Autoenv](https://github.com/kennethreitz/autoenv/), it will load for you the virtualenv when you `cd` the folder.

Then just start the webapp:
	
	$ ./webapp
