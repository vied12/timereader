Time Reader
===========

A reading companion for traveling by subway. 

Started in Paris, 2013 - Developed during the Open-data Hackathon for RATP.

Demo: http://timereader.herokuapp.com

## Pitch

Time Reader est une liseuse sur mobile, qui propose des contenus personnalisés et adaptés à vos temps de trajets. 

Pourquoi utiliser Time Reader ? Lorsque vous entrez un parcours, Time Reader calcule précisement la durée de votre trajets pour vous proposez des contenus qui correspondent votre temps de parcours. 

Profitez de vos déplacement en bus et en métro pour lire confortablement  : 

   * Vos bookmarks et podcasts sauvegardés dans Evernote, Pocket, Readability, Delicious ou Soundcloud
   * Des suggestions personnalisés d'articles et de podcasts, en fonction de vos centres d'intérêts (Culture, actualité, économie, sport, nouvelles technos, culture général... ).
   * Les articles partagés par les usagers de vos lignes de transport.

Dans le métro ou dans le bus, vous accédez d'un simple geste toutes les informations relatives à votre trajet (localisation, nombre de stations parcourues, temps de parcours, changements de lignes etc.). 

## Installation

### Dependances

	$ sudo apt-get install build-essential python-pip python-dev

and install virtualenv

	$ sudo pip install virtualenv

### Create a virtualenv and download dependances

	$ make install

#### No Python dependances

* [Mongodb](http://www.mongodb.org/)
* [CoffeeScript](http://coffeescript.org/)

### Launch

```
$ make run
```