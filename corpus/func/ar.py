from corpus.func import *

def main(args):
	items = args.items
	name = f'gkar_{"".join(items)}' #TODO name better
	array = f'{name}[] fillarray {", ".join(items)}'
	#orc_queue.put('score', array)

	return f"{name}[randomh:k(0, {len(items)}, 5)]"