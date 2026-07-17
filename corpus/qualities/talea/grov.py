from fractions import Fraction
from corpus.qualities.talea import *

def match(items: list) -> bool:
	if items[0] == 'grov':
		return True
	return False

#@auto_config(Talea)
def main(args):
	items = args.quality.items[1:]
	#UNRESOLVED: [QualityEntry(deduced=[1, 0, 1, 1, 1, 1, 1, 1], raws=['eu', '7', '8', 'in', '2'])] ['grov', '1']
	prev_talea = args.instrument.qualities['talea'].entries[-1].deduced
	args.instrument.qualities['talea'].entries[-1].deduced = list(expand(prev_talea, grooves=[float(Fraction(i)) for i in items]))
	args.instrument.qualities['talea'].dirty = True

def expand(pattern, grooves, target_length=128, curve=0.5):
	"""
	Expand binary pattern to target length by stretching each value into a block.
	Groove shifts the position of 1s within their step, in continuous space,
	rounded to a sample index only at the end. The first active step stays
	straight (no groove) so it can act as the anchor the groove is felt against.

	Args:
		pattern: list of 0s and 1s e.g. [1, 0, 1, 0]
		grooves: list of groove values in [-1, 1], cycled per active step
		target_length: total output length (default 64)
		curve: response curve exponent applied to groove magnitude before
			it's mapped to an offset. curve < 1 makes low groove values
			more audible sooner (expansive); curve > 1 makes low values
			more subtle and only "opens up" near the extremes (compressive);
			curve == 1 is the original linear response.

	Returns:
		list of 0s and 1s of length target_length
	"""
	pattern_len = len(pattern)
	step_width = target_length / pattern_len
	grooves_len = len(grooves)

	result = [0] * target_length
	groove_index = 0
	first_hit_seen = False

	for i, val in enumerate(pattern):
		if val != 1:
			continue

		step_start = i * step_width
		step_end = (i + 1) * step_width
		nominal = step_start + step_width / 2

		if not first_hit_seen:
			# anchor: no groove applied
			pos = 0
			first_hit_seen = True
		else:
			groove = grooves[groove_index % grooves_len]
			groove_index += 1

			# shape the response curve, preserving sign
			shaped_groove = (abs(groove) ** curve) * (1 if groove >= 0 else -1)

			offset = shaped_groove * (step_width / 2)
			pos = round(nominal + offset)

		# clamp so a grooved hit can't spill into a neighbouring step
		pos = max(int(step_start), min(int(step_end) - 1, pos))

		result[pos] = 1

	return result
