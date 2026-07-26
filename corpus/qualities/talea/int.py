from corpus.qualities.talea import *

def is_number(x):
	try:
		int(x)
		return True
	except (TypeError, ValueError):
		return False

def match(items: list) -> bool:
	if all(is_number(x) for x in items[0]):
		return True
	return False

@auto_config('cycle', 'talea')
def main(args):
	items = args.quality.items

	if 'in' in items:
		cycle = items[-1]
		items = items[:-2]
		talea = [1]*int(items[0])
	else:
		cycle = items[0]
		talea = [1]*8

	return str(cycle), talea
