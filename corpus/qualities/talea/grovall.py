from fractions import Fraction
from corpus.qualities.talea import *

stage = QualityStage.REFERENCE

def match(items: list) -> bool:
	if items[0] == 'grovall':
		return True
	return False

def main(args):
	items = args.quality.items[1:]

	all_values = args.instrument.talea.values
	args.instrument.talea.values = expand_groove(
		all_values, grooves=[float(Fraction(i)) for i in items], original_pattern_len=len([t.primary for t in args.instrument.talea])
	)
	args.instrument.talea.dirty = True

def expand_groove(pattern, grooves, original_pattern_len, curve=.5):
	pattern_len = len(pattern)
	groove_width = pattern_len / original_pattern_len
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
