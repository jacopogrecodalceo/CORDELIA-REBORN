from fractions import Fraction
from corpus.qualities.talea import *

stage = QualityStage.REFERENCE

def match(items: list) -> bool:
	if items[0] == 'grov':
		return True
	return False

def main(args):
	items = args.quality.items[1:]

	prev_talea = args.instrument.talea.prev
	args.instrument.talea.prev.processed = expand_groove(prev_talea.processed, grooves=[float(Fraction(i)) for i in items], length=len(prev_talea.primary))
	args.instrument.talea.dirty = True

def expand_groove(pattern, grooves, length, curve=.5):
	pattern_len = len(pattern)
	groove_width = pattern_len / length
	grooves_len = len(grooves)

	result = [0] * pattern_len
	groove_index = 0
	init_flag = True

	for i, val in enumerate(pattern):
		if val == 0:
			continue
		if init_flag:
			result[i] = 1
			init_flag = False
			continue

		center = groove_width / 2
		step_start = i - center
		step_end = i + center

		groove = grooves[groove_index % grooves_len]
		groove_index += 1

		# shape the response curve, preserving sign
		shaped_groove = (abs(groove) ** curve) * (1 if groove >= 0 else -1)

		offset = shaped_groove * (groove_width / 2)
		pos = round(step_start + offset)

		# clamp so a grooved hit can't spill into a neighbouring step
		pos = max(int(step_start), min(int(step_end) - 1, pos))
		result[pos] = 1
	return result
