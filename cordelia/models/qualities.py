import numpy as np
from dataclasses import dataclass, field
import itertools
from fractions import Fraction
import math
import abjad

from cordelia.const import TALEA_RESAMPLE_LEN, CYCLE_TARGET_DURATION, CYCLE_TARGET_LENGTH

@dataclass(slots=True)
class Quality:
	verse: list = field(default_factory=list)
	reference: list = field(default_factory=list)
	func: list = field(default_factory=list)
	primary: list = field(default_factory=list)
	processed: list = field(default_factory=list)


@dataclass(slots=True)
class SharedQuality:
	occurrencies: list[Quality] = field(default_factory=list)
	values: list = field(default_factory=list)
	dirty: bool = False

	def add(self, value, args):
		quality = Quality(
			verse=args.quality,
			func=[args.func],
			primary=value,
		)
		self.occurrencies.append(quality)

	def primary_process(self):
		if not self.occurrencies:
			self.occurrencies.append(Quality(primary=self.default_value))
		for quality in self.occurrencies:
			quality.processed = quality.primary

	def post_process(self):
		for quality in self.occurrencies:
			self.values.extend(quality.processed)

	@property
	def prev(self):
		return self.occurrencies[-1]

	def __iter__(self):
		for quality in self.occurrencies:
			yield quality

	def __len__(self):
		return len(self.occurrencies)

	def ftgen_format(self):
		return ', '.join(map(str, self.values))


@dataclass
class Cycle(SharedQuality):
   
	def parse_time_signatures(self, ts_strings: list[str]) -> list[abjad.TimeSignature]:
		"""Turn shorthand strings ('8', '7/8') into TimeSignature objects, defaulting to /4."""
		return [
			abjad.TimeSignature.from_string(ts if "/" in ts else f"{ts}/4")
			for ts in ts_strings
		]

	def build_segments(self, 
		signatures: list[abjad.TimeSignature], target: abjad.Duration
	) -> tuple[list[abjad.Duration], list[abjad.TimeSignature]]:
		"""Cycle through signatures, accumulating durations until target is reached,
		then append the overshoot as a final partial segment."""
		sig_cycle = itertools.cycle(signatures)
		segments: list[abjad.Duration] = []
		time_sigs: list[abjad.TimeSignature] = []
		total = abjad.Duration(0)

		while total < target:
			sig = next(sig_cycle)
			segments.append(sig.duration())
			time_sigs.append(sig)
			total += segments[-1]

		overshoot = total - target
		if overshoot > abjad.Duration(0):
			segments[-1] -= overshoot
			time_sigs[-1] = abjad.TimeSignature(((segments[-1]).numerator, (segments[-1]).denominator))
			total -= overshoot

		#used.append(sig)	used.append(next(sig_cycle))

		return segments, time_sigs


	def distribute_remainder(self, values: list[float], target_sum: int) -> list[int]:
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

	""" def compute_talea_y_values(self, instrument, used_signatures, segments):
		y_values = []
		count = 0

		taleae = [quality.primary for quality in self.occurrencies]
		talea_original_len = sum(len(t) for t in taleae)
		num_of_taleae = len(instrument.talea)
		for index, (sig, seg) in enumerate(zip(used_signatures, segments)):
			ratio = Fraction(float(sig.duration()) / float(seg)).limit_denominator()
			prev_count = count
			count += len(taleae[index % num_of_taleae])
			y_start = prev_count % talea_original_len
			y_end = count % talea_original_len
			if y_end == 0 and count > 0:
				y_end = talea_original_len
			y_values.append((math.floor(ratio * y_start), math.floor(ratio * y_end)))
		return y_values """



	def make_ts_breakpoints(self, instrument) -> list:
		"""Build a GEN -25-style breakpoint list (x0, 0, x1, y, x0, 0, x1, y, ...)
		mapping normalized durations to their time-signature ratio."""
		ts_strings = [c.processed for c in self.occurrencies]

		signatures = self.parse_time_signatures(ts_strings)
		#list[abjad.TimeSignature]
		segments, time_sigs = self.build_segments(signatures, CYCLE_TARGET_DURATION)

		total_duration = sum(segments)
		scaled = [float(seg) * CYCLE_TARGET_LENGTH / float(total_duration) for seg in segments]
		x_values = self.distribute_remainder(scaled, CYCLE_TARGET_LENGTH)

		y_values = self.compute_talea_y_values(instrument, time_sigs, segments)
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

	def test_break(self, instrument):
		ts_strings = [c.processed for c in self.occurrencies]

		signatures = self.parse_time_signatures(ts_strings)
		segments, time_sigs = self.build_segments(signatures, CYCLE_TARGET_DURATION)

		scale = CYCLE_TARGET_LENGTH / float(CYCLE_TARGET_DURATION)
		scaled = [float(seg) * scale for seg in segments]
		block_target_len = round(sum(scaled))
		x_values = self.distribute_remainder(scaled, block_target_len)

		lines = []
		x_sum = 0
		for i, x in enumerate(x_values):
			lines += [x_sum, i]
			x_sum += x

		return lines

	def ftgen_format(self, instrument):
		breakpoints = ', '.join(map(str, self.test_break(instrument)))
		return breakpoints

@dataclass
class Talea(SharedQuality):

	def _resample(self, talea, target_len=TALEA_RESAMPLE_LEN):
		"""zero pad resampling"""
		original_len = len(talea)
		result = [0] * target_len
		for old_index, value in enumerate(talea):
			if value:
				new_index = (old_index * target_len) // original_len
				result[new_index] = value
		return result
	def primary_process(self):
		for quality in self.occurrencies:
			quality.processed = self._resample(quality.primary)

	def prepare_GEN17(self):
		gen17 = []
		count = 1
		for i, v in enumerate(self.values):
			if v:
				x = i
				y = count
				gen17.extend([x, y, x+1, 0])
				count += 1
		return gen17

	""" def _count(self):
		count = 1
		result = []
		for quality in self.occurrencies:
			for v in quality.processed:
				v = int(v)
				if v > 0:
					result.append(count)
					count += 1
				else:
					result.append(v)
		return result """

	def ftgen_format(self):
		breakpoints = ', '.join(map(str, self.prepare_GEN17()))
		return breakpoints


@dataclass
class Color(SharedQuality):
	default_value: list = field(default_factory=lambda: ['1'])

@dataclass
class Dur(SharedQuality):
	default_value: list = field(default_factory=lambda: ['1'])

@dataclass
class Dyn(SharedQuality):
	default_value: list = field(default_factory=lambda: ['mf'])
	def ftgen_format(self):
		return ', '.join([rf'${v}' for v in self.values])

@dataclass
class Env(SharedQuality):
	default_value: list = field(default_factory=lambda: ['cls'])
	def ftgen_format(self):
		return ', '.join([rf'gi{v}' for v in self.values])

@dataclass
class Space(SharedQuality):
	default_value: list = field(default_factory=lambda: ['0'])
