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
	if items[0] in cordelia.const.data['mode']:
		return True
	return False

def main(quality: Quality, instrument: Instrument):
	items = quality.items

	mode = items[0]

	# default
	origin = items[1]
	if any(char in items[2] for char in (".", "'")):
		origin += items[2]
		degrees = items[3:]
	else:
		degrees = items[2:]


	#if any of them has a letter means to treat as an interval
	for d in degrees:
		if any(c.isalpha() for c in d):
			print('is interval')

	mode_degrees = cordelia.const.data['mode'][mode]
	mode_len = len(mode_degrees)
	instrument.score['colores'] = [mode_degrees[(int(d)-1 if int(d) != 0 else 1)%mode_len] for d in degrees]
