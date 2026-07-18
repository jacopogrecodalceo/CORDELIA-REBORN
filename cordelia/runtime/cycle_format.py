from __future__ import annotations

import itertools
from fractions import Fraction
import math
import abjad

TARGET_DURATION = abjad.Duration(64, 4)
TARGET_LENGTH = 8192

def parse_time_signatures(ts_strings: list[str]) -> list[abjad.TimeSignature]:
	"""Turn shorthand strings ('8', '7/8') into TimeSignature objects, defaulting to /4."""
	return [
		abjad.TimeSignature.from_string(ts if "/" in ts else f"{ts}/4")
		for ts in ts_strings
	]


def build_segments(
	signatures: list[abjad.TimeSignature], target: abjad.Duration
) -> tuple[list[abjad.Duration], list[abjad.TimeSignature]]:
	"""Cycle through signatures, accumulating durations until target is reached,
	then append the overshoot as a final partial segment."""
	sig_cycle = itertools.cycle(signatures)
	segments: list[abjad.Duration] = []
	used: list[abjad.TimeSignature] = []
	total = abjad.Duration(0)

	while total < target:
		sig = next(sig_cycle)
		segments.append(sig.duration())
		used.append(sig)
		total += segments[-1]

	reminder = total - target
	if reminder > abjad.Duration(0):
		segments.append(reminder)
	#used.append(sig)	used.append(next(sig_cycle))

	return segments, used


def distribute_remainder(values: list[float], target_sum: int) -> list[int]:
	"""Largest remainder method: floor each value, then hand out the
	leftover units to the entries with the biggest fractional part."""
	floors = [int(v) for v in values]
	remainder = target_sum - sum(floors)

	fractional_parts = [v - f for v, f in zip(values, floors)]
	order = sorted(range(len(values)), key=lambda i: fractional_parts[i], reverse=True)

	result = floors.copy()
	for i in order[:remainder]:
		result[i] += 1

	return result

def compute_talea_y_values(instrument, used_signatures, segments):
	"""Build (start, end) cumulative pairs per segment for a staircase shape,
	wrapping the visible count at talea_resolved_len."""
	y_values = []
	count = 0
	talea_resolved_len = len(instrument.qualities['talea'].resolved)
	entries_len = len(instrument.qualities['talea'].entries)
	for index, (sig, seg) in enumerate(zip(used_signatures, segments)):
		ratio = Fraction(float(sig.duration()) / float(seg)).limit_denominator()
		prev_count = count
		count += len(instrument.qualities['talea'].entries[index % entries_len].deduced)
		y_start = prev_count % talea_resolved_len
		y_end = count % talea_resolved_len
		if y_end == 0 and count > 0:
			y_end = talea_resolved_len
		y_values.append((math.floor(ratio * y_start), math.floor(ratio * y_end)))
	return y_values

def make_ts_breakpoints(instrument) -> list:
	"""Build a GEN -25-style breakpoint list (x0, 0, x1, y, x0, 0, x1, y, ...)
	mapping normalized durations to their time-signature ratio."""
	ts_strings = instrument.qualities['cycle'].resolved

	signatures = parse_time_signatures(ts_strings)
	segments, used_signatures = build_segments(signatures, TARGET_DURATION)

	total_duration = sum(segments)
	scaled = [float(seg) * TARGET_LENGTH / float(total_duration) for seg in segments]
	x_values = distribute_remainder(scaled, TARGET_LENGTH)

	y_values = compute_talea_y_values(instrument, used_signatures, segments)
	""" count = 0
	entries_len = len(instrument.qualities['talea'].entries)
	talea_resolved_len = len(instrument.qualities['talea'].resolved)
	for index, (sig, seg) in enumerate(zip(used_signatures, segments)):
		ratio = Fraction(float(sig.duration()) / float(seg)).limit_denominator()
		count += len(instrument.qualities['talea'].entries[index%entries_len].deduced)
		y_values.append(ratio*(count%talea_resolved_len)) """

	lines = []
	x_sum = 0
	prev_value = 0
	for x, (y_start, y_end) in zip(x_values, y_values):
		lines += [prev_value, str(y_start), x + x_sum, str(y_end)]
		prev_value = x + x_sum + 1
		x_sum += x

	return lines


def format_cycle_ftgen(instrument, ft_num: int) -> str:
	"""Render the ftgen line for an instrument's cycle table."""
	uid = instrument.uid
	breakpoints = ', '.join(map(str, make_ts_breakpoints(instrument)))
	return f'gi{uid}_cycle ftgen {ft_num}, 0, giFTGEN_SIZE, -27, {breakpoints}'


if __name__ == '__main__':
   v1 = make_ts_breakpoints(['2/4'])
   v2 = make_ts_breakpoints(['2/4', '2/4'])
   print(v1)
