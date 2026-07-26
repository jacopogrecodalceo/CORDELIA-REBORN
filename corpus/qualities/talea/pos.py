from corpus.qualities.talea import *

def match(items: list) -> bool:
	if items[0] == 'pos':
		return True
	return False

@auto_config('cycle', 'talea')
def main(args):
	items = args.quality.items

	items = items[1:]
	if 'in' in items:
		cycle = items[-1]
		rest = items[:-2]
		length = rest[-1]
		onsets = rest[:-1]
	else:
		length = items[-1]
		onsets = items[:-1]
		cycle = 8

	return str(cycle), [1 if str(i) in onsets else 0 for i in range(int(length))]