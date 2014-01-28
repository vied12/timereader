# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Time Reader
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 27-Jan-2014
# Last mod : 27-Jan-2014
# -----------------------------------------------------------------------------

angular.module('timereader', [])
    .controller 'ConfigCtrl',
      	class ConfigCtrl
        	time : 10
        	loadReader: ->

# EOF