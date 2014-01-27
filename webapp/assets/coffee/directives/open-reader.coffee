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

angular.module('timeReader')
  .directive 'openReader', () ->
    console.log coucou
    (scope, elem, attrs) ->
      console.log "coucou", scope, elem, attrs
      # elem.bind 'keydown', (e) ->
      #   if e.keyCode is 13
      #     $timeout ->
      #       scope.$apply attrs.enterKey
      #     , +attrs.enterKeyDelay

# EOF