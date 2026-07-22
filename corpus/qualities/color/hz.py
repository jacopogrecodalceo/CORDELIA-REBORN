from corpus.qualities.color import *

def match(items: list) -> bool:
	if items[0] in ('hz'):
		return True
	return False

@auto_config('color')
def main(args):
	items = args.quality.items[1:]

	values = [f for f in items if float(f) < 17500]

	return values