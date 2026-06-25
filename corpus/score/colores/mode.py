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
	if items[0] in cordelia.const.data.modes:
		return True
	return False

def main(items: list) -> Colores:
	mode = items[0]

	# default
	origin = 'b'
	degrees = [random.randint(-9, 9)]*12
	
	# Parse remaining arguments
	if len(items) == 2:
		origin = items[1]
	elif len(items) > 2:
		degrees = items[1:]
	
	return Colores(degrees)

if __name__ == '__main__':
	verse = "dorian"
	res = main(verse) 
	print(res)