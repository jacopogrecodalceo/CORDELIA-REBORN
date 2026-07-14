"""
=========================================

MATCHES
-------
	dorian        → explicit mode

RETURNS
-------
	Colores(pattern=[1,0,0,1,0,0,1,0], cycle=8)
"""

from corpus.qualities.color import *
from cordelia.registry.data import data

def match(items: list) -> bool:
	if items[0] in data['mode']:
		return True
	return False

@auto_config(Color)
def main(args):
	items = args.quality.items

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

	mode_degrees = data['mode'][mode]
	mode_len = len(mode_degrees)
	res = [mode_degrees[(int(d)-1 if int(d) != 0 else 1)%mode_len] for d in degrees]
	return res
