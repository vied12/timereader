Time Reader
===========

A reading companion for traveling by subway. 

Paris 2013 - Developed during the Open-data Hackathon for RATP. 

Demo: http://timereader.herokuapp.com

## Pitch

Time Reader est une liseuse sur mobile, qui propose des contenus personnalisés et adaptés à vos temps de trajets. 

Pourquoi utiliser Time Reader ? Lorsque vous entrez un parcours, Time Reader calcule précisement la durée de votre trajets pour vous proposez des contenus qui correspondent votre temps de parcours. 

Profitez de vos déplacement en bus et en métro pour lire confortablement  : 

   * Vos bookmarks et podcasts sauvegardés dans Evernote, Pocket, Readability, Delicious ou Soundcloud
   * Des suggestions personnalisés d'articles et de podcasts, en fonction de vos centres d'intérêts (Culture, actualité, économie, sport, nouvelles technos, culture général... ).
   * Les articles partagés par les usagers de vos lignes de transport.

Dans le métro ou dans le bus, vous accédez d'un simple geste toutes les informations relatives à votre trajet (localisation, nombre de stations parcourues, temps de parcours, changements de lignes etc.). 

## The application

This application run with:
* Python 2.7
* Flask 0.9
* Mongodb

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

	$ pip install -r requirements.txt

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
