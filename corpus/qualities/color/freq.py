from corpus.qualities.color import *

stage = QualityStage.REFERENCE

def match(items: list):
	if items[0] == 'freq':
		return True
	return False

def main(args):
	items = args.quality.items[1:]
	quality = getattr(args.instrument, 'color')
	math_op = items[0]

	values = items[1] if isinstance(items[1], list) else items[1:]

	prev_values = [v for occurrence in quality for v in occurrence.processed]
	target = max(len(prev_values), len(values))

	i = 0
	while i < target:
		for occurrence in quality:
			prev = prev_values[i % len(prev_values)]
			value = values[i % len(values)]
			result = f'{prev}{math_op}{value}'
			if i < len(occurrence.processed):
				occurrence.processed[i] = result
			else:
				occurrence.processed.append(result)
			i += 1
	quality.dirty = True