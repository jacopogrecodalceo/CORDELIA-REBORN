from itertools import cycle

from corpus.qualities.talea import *

def match(items: list) -> bool:
	if items[0].isdigit():
		return True
	return False

@auto_config(Cycle, Talea)
def main(args):
	items = args.quality.items

	val = items[0]

	res = [1]*int(val)
	cycle = val

	return cycle, res