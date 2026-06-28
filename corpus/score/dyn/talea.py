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
from corpus.score.dyn import *
import cordelia.const

def match(items: list) -> bool:
	if items[0] in cordelia.const.data['dyn']:
		return True
	return False

def main(quality: Quality, instrument: Instrument) -> Dyn:
	items = quality.items
	validate(items)
	instrument.score['dyn'] = items

def validate(items: list) -> bool:
	for i in set(items):
		if i not in cordelia.const.data['dyn']:
			raise ValueError(f"{i} does not belong to dyns!!")

