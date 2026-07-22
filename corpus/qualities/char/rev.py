from corpus.qualities import *

stage = QualityStage.REFERENCE

def match(items: list) -> bool:
	if items[0] in 'rev':
		return True
	return False

def main(args):
	#items = quality.items
	items = args.quality.items[1:]

	prev_talea = args.instrument.talea.prev
	args.instrument.talea.dirty = True

