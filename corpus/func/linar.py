from cordelia.registry import orc_queue
from pathlib import Path
from corpus.func import *

func_name = Path(__name__).stem

def main(args):
	items = args.items
	name = f'gk{func_name}_{args.instrument.name}' #TODO name better
	array = f'{name}[] fillarray {", ".join(items)}'
	orc_queue.put('variable', array)

	return f"{name}[phasor:k()*{len(items)}]"