"""
=========================================

MATCHES
-------
	dorian        → explicit mode

RETURNS
-------
	Colores(pattern=[1,0,0,1,0,0,1,0], cycle=8)
"""

import cordelia.const
from corpus.score.colores import *

def match(items: list) -> bool:
	if items[0] in ('hz', 'freq'):
		return True
	return False

def main(quality: Quality, instrument: Instrument):
	items = quality.items

	args = items[1:]

	# default
	instrument.score['colores'] = args

