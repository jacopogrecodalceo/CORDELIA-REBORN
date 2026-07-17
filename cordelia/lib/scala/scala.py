# litchi/lib/tuning/scale.py

"""
Core Scale value object. Construction, pitch-class mapping, and note
resolution are delegated to focused collaborators (scale_builders,
pitch_class_map, NoteResolver) so each concern evolves independently.
"""

from dataclasses import dataclass, field

import abjad

from cordelia.lib.scala.note_resolver import NoteResolver
from cordelia.lib.scala.pitch_class_map import build_pitch_class_map
from cordelia.lib.scala.scala_builders import SCALE_BUILDERs


@dataclass
class Scala:
	origin_value: str | int | float
	quarter_tones: bool = False
	compensate: bool = False

	name: str | None = field(init=False, default=None)
	values: list = field(default_factory=list)
	chromatic_intervals: dict = field(default_factory=lambda: {num: [] for num in range(12)})

	denominator_limit: int = int(1e5)
	tolerance: int = 6

	def __post_init__(self):
		if isinstance(self.origin_value, str) and self.origin_value[0].isalpha():
			self.origin_numbered_pitch = abjad.NumberedPitch(self.origin_value)
			self.origin_decimal_value = self.origin_numbered_pitch.hertz
		elif isinstance(self.origin_value, (int, float)):
			self.origin_numbered_pitch = abjad.NumberedPitch.from_hertz(self.origin_value)
			self.origin_decimal_value = self.origin_value
		self.hertz = self.origin_decimal_value

	def build(self, builder_name: str, name: str = None, **kwargs):
		"""
		Generic entry point for any registered construction strategy, e.g.
		scale.build('edo', n=31) or scale.build('scala', scala_name='partch_43').
		"""
		builder = SCALE_BUILDERS[builder_name]
		self.values = builder(**kwargs)
		self.values.insert(0, 1)
		if self.values[-1] == 2:
			self.values.pop(-1)
		self.name = name or f'{builder_name}-{"-".join(str(v) for v in kwargs.values())}'
		return self.values

	# Thin, backward-compatible wrappers over build():
	def edo(self, n: int):
		return self.build('edo', name=f'edo{n}', n=n)

	def edolin(self, n: int):
		return self.build('edolin', name=f'harm{n}-edolin', n=n)

	def evoke(self, scala_name: str):
		return self.build('scala', name=scala_name, scala_name=scala_name)

	def make(self):
		"""Computes the chromatic pitch-class map from self.values."""
		assert self.values[0] == 1, "WARNING: First value is not 1."
		self.chromatic_intervals = build_pitch_class_map(
			self.values,
			self.origin_numbered_pitch,
			self.denominator_limit,
			quarter_tones=self.quarter_tones,
		)
		assert self.values

	def resolver(self, **kwargs) -> NoteResolver:
		"""
		Returns a NoteResolver bound to this scale. kwargs forwarded to
		NoteResolver for injecting custom on_missing_interval /
		on_frequency_mismatch callbacks.
		"""
		return NoteResolver(scale=self, **kwargs)

	def get_interval(self, string: str, transpose=0, print_modulo=True):
		"""Backward-compatible shortcut for resolver().resolve(...)."""
		return self.resolver(print_modulo=print_modulo).resolve(string, transpose=transpose)

	def __repr__(self):
		attributes = {
			"name": self.name,
			"origin_value": self.origin_value,
			"origin_numbered_pitch": self.origin_numbered_pitch.name,
			"denominator_limit": self.denominator_limit,
			"tolerance": self.tolerance,
		}
		attr_strings = [f"    {name:<20} = {value}" for name, value in attributes.items()]
		attr_strings_str = ",\n".join(attr_strings)
		return f"Scale(\n{attr_strings_str}\n)"
