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
from corpus.score.env import *
import cordelia.const

def match(items: list) -> bool:
	if items[0] in cordelia.const.data['env']:
		return True
	return False

@auto_config(Env)
def main(args):
	items = args.quality.items

	validate(items)
	return items

def validate(items: list) -> bool:
	for i in set(items):
		if i not in cordelia.const.data['env']:
			raise ValueError(f"{i} does not belong to fts!!")