"""
=========================================
talea is a talea function
1. the first arg is always "talea" that's also the main deduction for this function 
2. it is an array but 
	-	rest is 0
	-	negative number is rest x duration (this means that 0 == -1)
3. the time is always at the end after the first "in" if there's no "in" in the last one before. it is automatically set
MATCHES
-------
	eu 3 8        → explicit keyword
	3 8           → two integers, inferred as euclidean

RETURNS
-------
	Talea(pattern=[1,0,0,1,0,0,1,0], cycle=8)
"""
from corpus.qualities.talea import *

def match(items: list) -> bool:
	if items[0] == 'talea':
		return True
	return False

@auto_config(Cycle, Talea)
def main(args) -> Talea:

	args = args.quality.items[1:]
	pulse_values = []
	cycle = None
	i = 0

	while i < len(args):
		token = args[i]

		if token == 'in':
			if i + 1 >= len(args):
				raise ValueError("'in' requires a duration argument")
			cycle = args[i + 1]   
			break

		if token == '-' and i + 1 < len(args):
			token = f'-{args[i + 1]}'
			i += 1

		v = int(token)
		if v > 0:
			pulse_values.append(1)
			pulse_values.extend([0] * (v - 1))
		elif v == 0:
			pulse_values.append(0)
		else:
			pulse_values.extend([0] * abs(v))

		i += 1

	if cycle is None:
		raise ValueError("talea requires an 'in' clause with a duration")

	return cycle, pulse_values