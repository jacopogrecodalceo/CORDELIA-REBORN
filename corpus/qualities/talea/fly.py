import random
from corpus.qualities.talea import *
from cordelia.const import TALEA_RESAMPLE_LEN

resample_length = (TALEA_RESAMPLE_LEN) // 2

stage = QualityStage.REFERENCE

def match(items: list) -> bool:
	if items[0] == 'fly':
		return True
	return False

def main(args):
	items = args.quality.items

	items = args.quality.items[1:]

	prev_talea = args.instrument.talea.prev
	args.instrument.talea.prev.processed = cauchy_binary([i for i, v in enumerate(prev_talea.primary) if int(v) > 0], len(prev_talea.primary), items)
	args.instrument.talea.dirty = True

def cauchy_curve(length, center_index, gamma):
	values = []
	for i in range(length):
		values.append(1 / (1 + ((i - center_index) / gamma) ** 2))
	return values

def cauchy_binary(onsets, length, gammas):
	combined = [0] * resample_length
	for i, onset in enumerate(onsets):
		index = resample_length / length * float(onset)
		curve = cauchy_curve(resample_length, index, float(gammas[i%len(gammas)])*2)
		for i, v in enumerate(curve):
			combined[i] = max(combined[i], v)
	res = [1 if random.random() < v else 0 for v in combined]
	i = 1
	while len(res) < TALEA_RESAMPLE_LEN:
		res.insert(i, 0)
		i += 2
	return res

