# litchi/lib/tuning/note_resolver.py

"""
Resolves LilyPond-style note strings (e.g. "b0", "cs-2") against a
Scale's pitch-class map.

Both failure cases that used to call input() directly - a missing
interval and a frequency mismatch - now go through injectable
callbacks. Defaults reproduce the original blocking y/n prompts, so
nothing changes for a script run at the REPL. But a caller running
this from Cordelia's performance thread can pass its own callbacks
(log and skip, auto-compensate, raise) instead of freezing on stdin.
"""

import re
from dataclasses import dataclass
from decimal import Decimal

import abjad


class NoIntervalFoundError(Exception):
	pass


class FrequencyMismatchError(Exception):
	pass


def parse_lilypond_note(string: str) -> tuple[str, int]:
	"""
	Splits a Cordelia note string into its LilyPond pitch name and the
	trailing interval-degree number, e.g. "a'40" -> ("a'", 40).
	"""
	match = re.search(r'(-?\d+)', string)
	if not match:
		return string, 0
	position = match.start()
	return string[:position], int(string[position:])


def default_on_missing_interval(pitch_class_offset, scale_name) -> bool:
	"""Return True to attempt compensation, False to skip the note."""
	response = input(
		f"In {scale_name} no interval found for pitch class {pitch_class_offset}, want me to compensate? (y/n): "
	)
	return response.strip().lower() == 'y'


def default_on_frequency_mismatch(numbered_pitch, expected_freq, got_freq, difference):
	print("Warning: Frequency difference exceeds threshold:")
	print(f"Note: {numbered_pitch.name}")
	print(f"Expected: {expected_freq} Hz")
	print(f"Got: {got_freq} Hz")
	print(f"Difference: {difference} Hz")
	response = input("Continue anyway? (y/n): ").strip().lower()
	if response != 'y':
		raise FrequencyMismatchError(f"Aborted on {numbered_pitch.name} frequency mismatch.")


@dataclass
class NoteResolver:
	scale: 'litchi.lib.tuning.scale.Scale'
	on_missing_interval: callable = default_on_missing_interval
	on_frequency_mismatch: callable = default_on_frequency_mismatch
	mismatch_tolerance: Decimal = Decimal('0.1')
	print_modulo: bool = True

	def resolve(self, string: str, transpose: int = 0):
		ly_named_pitch_string, selected_interval_number = parse_lilypond_note(string)
		ly_numbered_pitch = (
			abjad.NumberedPitch(ly_named_pitch_string)
			if transpose == 0
			else abjad.NumberedPitch(ly_named_pitch_string).transpose(transpose)
		)

		semitone_distance = ly_numbered_pitch.number - self.scale.origin_numbered_pitch.number
		octaves = semitone_distance // 12
		pitch_class_offset = ly_numbered_pitch.pitch_class.number
		candidates = self.scale.chromatic_intervals[pitch_class_offset]

		if not candidates:
			should_compensate = self.scale.compensate or self.on_missing_interval(pitch_class_offset, self.scale.name)
			if not should_compensate:
				return None
			self.scale.compensate = True
			ly_numbered_pitch, octaves, pitch_class_offset, candidates = self._compensate(
				ly_named_pitch_string, transpose
			)

		selected_interval = candidates[selected_interval_number % len(candidates)]

		if selected_interval_number >= len(candidates) and self.print_modulo:
			print('NO VALUE, MODULO ENABLED!')

		selected_interval.pitch = ly_numbered_pitch
		selected_interval.freq = (
			Decimal(self.scale.origin_decimal_value)
			* Decimal(selected_interval.value)
			* (Decimal(2) ** Decimal(octaves))
		)

		self._check_frequency(ly_numbered_pitch, selected_interval)
		return selected_interval

	def _compensate(self, ly_named_pitch_string, transpose):
		index_transposition = 1
		while index_transposition <= 12:
			ly_numbered_pitch = abjad.NumberedPitch(ly_named_pitch_string).transpose(transpose + index_transposition)
			semitone_distance = ly_numbered_pitch.number - self.scale.origin_numbered_pitch.number
			octaves = semitone_distance // 12
			pitch_class_offset = ly_numbered_pitch.pitch_class.number
			candidates = self.scale.chromatic_intervals[pitch_class_offset]

			if candidates:
				return ly_numbered_pitch, octaves, pitch_class_offset, candidates

			index_transposition += 1

		raise NoIntervalFoundError("Could not compensate: no interval found within 12 transpositions.")

	def _check_frequency(self, ly_numbered_pitch, selected_interval):
		difference = abs(Decimal(ly_numbered_pitch.hertz) - selected_interval.freq)
		threshold = Decimal(ly_numbered_pitch.hertz) * self.mismatch_tolerance

		if difference >= threshold:
			self.on_frequency_mismatch(ly_numbered_pitch, ly_numbered_pitch.hertz, selected_interval.freq, difference)