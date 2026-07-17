import re
import abjad
from pathlib import Path
from bisect import bisect_left

from cordelia.lib.scala.parse import get_frequencies, expand_to_range
from corpus.qualities.color import *
from cordelia.registry.data import data

def match(items: list) -> bool:
	if items[0] in data['scala']:
		return True
	return False

@auto_config(Color)
def main(args):
	"""
	e.g.
	pto_diat d. 1 3m 5
	"""
	items = args.quality.items

	scala = items[0]

	origin = items[1]
	if origin[0].isalpha():
		origin_pitch = abjad.NamedPitch(origin.replace('.', ','))
		degrees = items[2:]
	else:
		origin_pitch = abjad.NamedPitch('c')
		degrees = items[1:]
	origin_pitch += abjad.NumberedInterval(12)

	scala_path = Path(data['scala'][scala])
	freqs = get_frequencies(scala_path.read_text())
	scala_freqs = expand_to_range(freqs)

	res = []
	for degree in degrees:
		st = interval_to_semitones(degree)
		target = origin_pitch+abjad.NumberedInterval(st)
		res.append(find_nearest(target.hertz(), scala_freqs))

	return res

def interval_to_semitones(interval_name):
	"""Return total semitones for a simple or compound interval, e.g. '9' -> 14, '-10m' -> -15."""
	match = re.match(r"(-?)(\d+)(.*)", interval_name.strip())
	sign = -1 if match.group(1) == "-" else 1
	degree = int(match.group(2))
	quality = match.group(3)

	octave_offset = (degree - 1) // 7
	reduced_degree = ((degree - 1) % 7) + 1
	reduced_name = f"{reduced_degree}{quality}"

	semitones = data['degree'][reduced_name] + 12 * octave_offset
	return sign * semitones

def find_nearest(target, sorted_values):
	"""Return the value in sorted_values closest to target. Assumes sorted ascending."""
	index = bisect_left(sorted_values, target)

	if index == 0:
		return sorted_values[0]
	if index == len(sorted_values):
		return sorted_values[-1]

	before = sorted_values[index - 1]
	after = sorted_values[index]

	if after - target < target - before:
		return after
	return before

