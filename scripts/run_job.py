#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Time Reader
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 08-Jul-2013
# Last mod : 08-Jul-2013
# -----------------------------------------------------------------------------

from worker import Worker
import sys

worker = Worker(async=False)

if __name__ == "__main__":
	worker.run(*sys.argv[1:])

# EOF
