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
from corpus.qualities.dyn import *
import cordelia.const

data = cordelia.const.data.dyns
print(data)
def match(items: list) -> bool:
	if items[0] in data:
		return True
	return False

def dyn(items: list) -> Dyn:
	validate(items)
	print(items)
	return Dyn([cordelia.const.data.file('dyns')[i]['norm'] for i in items])

def validate(items: list) -> bool:
	for i in set(items):
		if i not in data:
			raise ValueError(f"{i} does not belong to fts!!")