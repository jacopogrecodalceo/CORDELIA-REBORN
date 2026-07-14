"""
=========================================

MATCHES
-------
	eu 3 8        → explicit keyword
	3 8           → two integers, inferred as euclidean

RETURNS
-------
	Talea(pattern=[1,0,0,1,0,0,1,0], cycle=8)
"""

from corpus.qualities import *
from cordelia.registry.data import data

data = data['dyn']

def match(items: list) -> bool:
	if items[0] in 'stubborn':
		return True
	return False

@auto_config(Char)
def main(args):
	#items = quality.items
	return 'stubborn'

