from dataclasses import dataclass, field
import itertools
import abjad

from cordelia.const import FTGEN_SIZE, TALEA_RESAMPLE_LEN, CYCLE_TARGET_DURATION, FTGEN_SIZE

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
			primary=value
		)
		self.occurrencies.append(quality)

	def remove_default_values(self):
		for occurrency in self.occurrencies:
			if not occurrency.verse and not occurrency.func:
				self.occurrencies = []

	def copy(self, quality: Quality):
		self.remove_default_values()
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
	default_value: list = field(default_factory=lambda: ['8'])

	def parse_signatures(self, ts_strings: list[str]) -> list[abjad.TimeSignature]:
		"""Turn shorthand strings ('8', '7/8') into TimeSignature objects, defaulting to /4."""
		return [
			abjad.TimeSignature.from_string(ts if "/" in ts else f"{ts}/4")
			for ts in ts_strings
		]

	def segment_cycle_to_target(
		self, signatures: list[abjad.TimeSignature], target: abjad.Duration
	) -> tuple[list[abjad.Duration], list[abjad.TimeSignature]]:
		"""Cycle through signatures, accumulating durations until target is reached,
		then trim the final segment so the total lands exactly on target."""
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
			time_sigs[-1] = abjad.TimeSignature((segments[-1].numerator, segments[-1].denominator))

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

	def build_breakpoints(self, scale: float) -> list:
		"""Build a flat GEN-style breakpoint list (x0, y0, x1, y1, ...) where each
		x marks a segment boundary and y is that segment's index in the cycle."""
		ts_strings = [c.processed for c in self.occurrencies]
		signatures = self.parse_signatures(ts_strings)
		segments, _ = self.segment_cycle_to_target(signatures, CYCLE_TARGET_DURATION)

		scaled = [float(seg) * scale for seg in segments]
		block_target_len = round(sum(scaled))
		x_values = self.distribute_remainder(scaled, block_target_len)

		lines = []
		x_sum = 0
		for index, x in enumerate(x_values):
			lines += [x_sum, index]
			x_sum += x

		lines += [x_sum, len(x_values)]  # close the table at the true end
		return lines

	def ftgen_format(self) -> str:
		scale = FTGEN_SIZE / float(CYCLE_TARGET_DURATION)
		breakpoints = self.build_breakpoints(scale)
		return ', '.join(map(str, breakpoints))


@dataclass
class Talea(SharedQuality):
	default_value: list = field(default_factory=lambda: ['8'])

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
		ftgen = []
		count = 1
		for i, v in enumerate(self.values):
			if v:
				x = i
				y = count
				ftgen.extend([x, y, x+1, 0])
				count += 1
		if ftgen[0] != 0:
			ftgen.insert(0, 0)
			ftgen.insert(0, 0)
		return ftgen

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
		vs = []
		for v in self.values:
			if isinstance(v, str) and all(x.isalpha() for x in v):
				vs.append(f'${v}')
			else:
				vs.append(v)
				
		return ', '.join(map(str, vs))

@dataclass
class Env(SharedQuality):
	default_value: list = field(default_factory=lambda: ['env'])
	def ftgen_format(self):
		return ', '.join([rf'gi{v}' for v in self.values])

@dataclass
class Space(SharedQuality):
	default_value: list = field(default_factory=lambda: ['0'])
