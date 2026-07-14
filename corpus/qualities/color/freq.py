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

def match(items: list) -> bool:
	if items[0] in ('hz', 'freq'):
		return True
	return False

@auto_config(Color)
def main(args):
	items = args.quality.items

	values = [f for f in items[1:] if float(f) < 17500]

	# default
	return values
