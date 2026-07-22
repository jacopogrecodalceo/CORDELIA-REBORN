from fractions import Fraction
from corpus.func import *

def main(args):
	items = args.items

	if len(items) == 3:
		amp   = items[0]
		freq_min = items[1]
		freq_max = items[2]

	elif len(items) == 2:
		amp   = items[0]
		freq_min = items[1]
		freq_max = Fraction(freq_min)/8

	else:
		amp   = items[0]
		freq_min = 1
		freq_max = freq_min/8

	packed = [amp, freq_min, float(freq_max)]

	return f"jitter({', '.join(map(str, packed))})"