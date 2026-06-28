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
from corpus.score.character import *
import cordelia.const

data = cordelia.const.data['dyn']

def match(items: list) -> bool:
	if items[0] in 'stubborn':
		return True
	return False

def main(quality: Quality, instrument: Instrument) -> Character:
	#items = quality.items
	instrument.score['characters'] = ['stubborn']

