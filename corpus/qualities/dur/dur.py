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
from corpus.qualities.dur import *

def match(items: list) -> bool:
	if items[0].startswith('dur') or items[0] == 'dur':
		return True
	return False

def dur(items: list) -> Dur:
	if items[0].startswith('dur'):
		return Dur([1])
	elif items[0] == 'dur':
		args = items[1:]
		return Dur([2])
