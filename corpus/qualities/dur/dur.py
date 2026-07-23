from corpus.qualities.color import *

stage = QualityStage.REFERENCE

def match(items: list):
	if items[0] == 'dur':
		return True
	return False

def main(args):
	items = args.quality.items[1:]
	if isinstance(items[1], list):
		for occurrence in args.instrument.dur:
			math_op = items[0]
			values = items[1]
			#entry.deduced = [eval(f'{f}{math_op}{values[i%len(values)]}') for i, f in enumerate(entry.deduced)]
			occurrence.processed = [eval(f'{f}{math_op}{values[i%len(values)]}') for i, f in enumerate(occurrence.processed)]
	else:
		for occurrence in args.instrument.dur:
			occurrence.processed = [eval(f'{f}{"".join(items)}') for f in occurrence.processed]
	args.instrument.dur.dirty = True

