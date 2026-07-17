# litchi/lib/tuning/interval.py

import math
from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction

from cordelia.lib.scala.named_interval_matcher import IntervalNamer

EDO12_LOG2 = Decimal(1200 / math.log10(2))


@dataclass
class Interval:
	"""
	A single tuned interval above a scale's origin. Pure value object:
	no knowledge of Scale, pitch classes, or notation - just the math
	and the (optional) named-interval lookup.
	"""

	value: float
	denominator_limit: int
	tolerance: int = 6
	namer: IntervalNamer | None = None

	name: str | None = field(init=False, default=None)
	interval_name_ratio: str | None = field(init=False, default=None)
	cents: str | None = field(init=False, default=None)
	abs_cents: Decimal | None = field(init=False, default=None)
	semitones: Decimal | None = field(init=False, default=None)
	ratio: Fraction | None = field(init=False, default=None)

	def process(self):
		log_value = Decimal(math.log10(float(self.value)))
		self.abs_cents = log_value * EDO12_LOG2
		self.semitones = self.abs_cents / 100
		self.ratio = Fraction(float(self.value)).limit_denominator(int(self.denominator_limit))

		namer = self.namer if self.namer is not None else IntervalNamer(max_tolerance=self.tolerance)
		match = namer.match(self.ratio)
		if match:
			self.name = match.name
			self.interval_name_ratio = match.interval_name_ratio

	def __repr__(self):
		attributes = {
			"value": self.value,
			"denominator_limit": self.denominator_limit,
			"name": self.name,
			"cents": self.cents,
			"tolerance": self.tolerance,
			"abs_cents (rounded)": round(self.abs_cents, 2) if self.abs_cents is not None else None,
			"semitones (rounded)": round(self.semitones, 2) if self.semitones is not None else None,
			"ratio": self.ratio,
			"interval_name_ratio": self.interval_name_ratio,
		}
		attr_strings = [f"    {name:<20} = {value}" for name, value in attributes.items()]
		attr_strings_str = ",\n".join(attr_strings)
		return f"Interval(\n{attr_strings_str}\n)"