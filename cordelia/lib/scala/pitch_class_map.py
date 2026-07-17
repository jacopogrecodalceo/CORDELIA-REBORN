# litchi/lib/tuning/pitch_class_map.py

"""
Maps a scale's raw interval values onto the twelve chromatic pitch
classes, so notation code can ask "give me the interval on pitch
class X" without knowing how the scale was built.
"""

import math

import abjad

from cordelia.lib.scala.interval import Interval
from cordelia.lib.scala.named_interval_matcher import IntervalNamer


def build_pitch_class_map(
	values: list,
	origin_numbered_pitch,
	denominator_limit: int,
	quarter_tones: bool = False,
	namer: IntervalNamer | None = None,
) -> dict:
	chromatic_intervals = {num: [] for num in range(12)}

	for value in values:
		interval = Interval(value, denominator_limit=denominator_limit, namer=namer)
		interval.process()

		decimal_part, integer_part = math.modf(float(interval.semitones))
		pitch = origin_numbered_pitch.number + int(integer_part)
		cents_from_written_pitch = round(decimal_part * 100)

		if integer_part < 11:
			if abs(cents_from_written_pitch) > 50:
				# treated differently so 11 doesn't rebounce onto 0
				pitch += 1 if cents_from_written_pitch > 0 else -1
				cents_from_written_pitch = (
					cents_from_written_pitch - 100 if cents_from_written_pitch > 0
					else cents_from_written_pitch + 100
				)

			if quarter_tones and abs(cents_from_written_pitch) > 25:
				pitch += .5 if cents_from_written_pitch > 0 else -.5
				cents_from_written_pitch = (
					cents_from_written_pitch - 50 if cents_from_written_pitch > 0
					else cents_from_written_pitch + 50
				)

		interval.cents = f"{cents_from_written_pitch:+}¢" if cents_from_written_pitch != 0 else None
		interval.pitch_class_name = abjad.NamedPitch(int(pitch)).pitch_class.name
		interval.pitch_class_num = abjad.NamedPitch(int(pitch)).pitch_class.number

		chromatic_intervals[interval.pitch_class_num].append(interval)

	return chromatic_intervals