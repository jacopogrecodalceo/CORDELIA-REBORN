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

from corpus.score.dur import *

def match(items: list) -> bool:
	if items[0].startswith('dur') or items[0] == 'dur':
		return True
	return False

def main(quality: Quality, instrument: Instrument):
	items = quality.items
	instrument.score['dur'] = items
