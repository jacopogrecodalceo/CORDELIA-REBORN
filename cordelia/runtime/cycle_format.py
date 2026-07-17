from __future__ import annotations

import itertools
from fractions import Fraction

import abjad

TARGET_DURATION = abjad.Duration(64, 4)
TARGET_LENGTH = 8192

def parse_time_signatures(ts_strings: list[str]) -> list[abjad.TimeSignature]:
	"""Turn shorthand strings ('8', '7/8') into TimeSignature objects, defaulting to /4."""
	parsed = []
	ts_len = len(ts_strings)
	for ts in ts_strings:
		if "/" in ts:
			ts = Fraction(ts)*ts_len
		else:
			ts = Fraction(f"{ts}/4")*ts_len	
		parsed.append(abjad.TimeSignature((ts.numerator, ts.denominator)))

	return parsed

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
	used.append(next(sig_cycle))

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


def make_ts_breakpoints(ts_strings: list[str]) -> list:
	"""Build a GEN -25-style breakpoint list (x0, 0, x1, y, x0, 0, x1, y, ...)
	mapping normalized durations to their time-signature ratio."""
	signatures = parse_time_signatures(ts_strings)
	segments, used_signatures = build_segments(signatures, TARGET_DURATION)

	total_duration = sum(segments)
	scaled = [float(seg) * TARGET_LENGTH / float(total_duration) for seg in segments]
	x_values = distribute_remainder(scaled, TARGET_LENGTH)

	y_values = [
		Fraction(float(sig.duration()) / float(seg)).limit_denominator()
		for sig, seg in zip(used_signatures, segments)
	]

	lines = []
	x_sum = 0
	prev_value = 0
	for x, y in zip(x_values, y_values):
		lines += [prev_value, 0, x + x_sum, str(y)]
		prev_value = x + x_sum + 1
		x_sum += x

	return lines


def format_cycle_ftgen(uid: str, ts_strings: list[str], ft_num: int) -> str:
	"""Render the ftgen line for an instrument's cycle table."""
	breakpoints = ', '.join(map(str, make_ts_breakpoints(ts_strings)))
	return f'gi{uid}_cycle ftgen {ft_num}, 0, giFTGEN_SIZE, -27, {breakpoints}'