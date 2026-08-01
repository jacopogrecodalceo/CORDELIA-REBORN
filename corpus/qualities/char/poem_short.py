import abjad
import random
from fractions import Fraction
from corpus.qualities import *

def match(items: list) -> bool:
	if items[0] == 'poem_short':
		return True
	return False

@auto_config('cycle', 'talea', 'color')
def main(args):
	items = args.quality.items[1:]

	string = ' '.join(items)
	notes = get_notes_from_string(string)
	transp = make_transposition(string, limits=(-1, 3))
	durations = fill_duration_s(string)

	res = []
	for i, r in enumerate(durations):
		dur = abjad.Duration(*Fraction(r).limit_denominator().as_integer_ratio())
		note = abjad.Note(notes[i + random.randint(0, 1) % len(notes)])
		note.set_written_duration(dur)
		abjad.mutate.transpose(note, 12 * transp[i % len(transp)])
		res.append(note)

	grain = min(1 / pow(2, x) for x in range(1, 6))
	onsets = durations_to_onsets(durations, grain)
	frequencies = notes_to_frequencies(res)

	return '8', onsets, frequencies

def durations_to_onsets(durations: list, grain: float) -> list:
	"""Expand a list of durations into a binary onset/sustain grid at grain resolution."""
	onsets = []
	for dur in durations:
		steps = round(dur / grain)
		onsets.append(1)
		onsets.extend([0] * (steps - 1))
	return onsets


def notes_to_frequencies(notes: list) -> list:
	"""Extract the frequency (Hz) of each note, after any transposition has been applied."""
	return [note.written_pitch().hertz() for note in notes]

NOTE_NAMEs = [abjad.NumberedPitchClass(i).name() for i in range(12)]

def get_notes_from_string(string, max_notes=None):

	if not max_notes:
		max_notes = len(string)

	def _get_notes(string, index=0):
		results = []

		if index == 0:
			# Forward and inverted two-letter combinations
			for i in range(len(string) - 1):
				a, b = string[i], string[i + 1]
				if a + b in NOTE_NAMEs:
					results.append(a + b)
				if b + a in NOTE_NAMEs:
					results.append(b + a)

			# Single-letter matches
			for c in string:
				if c in NOTE_NAMEs:
					results.append(c)

		else:
			# Shifted letters by index
			for i in range(len(string) - 1):
				a_shifted = chr(((ord(string[i]) - ord('a') + index) % 26) + ord('a'))
				b = string[i + 1]
				if a_shifted + b in NOTE_NAMEs:
					results.append(a_shifted + b)
				if b + a_shifted in NOTE_NAMEs:
					results.append(b + a_shifted)

		return results

	pool = []

	i = 0
	while len(pool) < max_notes:
		notes = _get_notes(string, index=i)
		print(f'{string}, index = {i} {pool} {NOTE_NAMEs}')
		if i > 200:  # stop if no more results
			raise ValueError("String has some problem.. it's the 200 times i tried..")
		pool.extend(notes)
		i += 1
	return pool

def make_transposition(string, limits=(-2, 2)):
	pool = []
	words = string.split()
	if len(words) > 1:
		for word in words:
			w_len = len(word)
			if w_len > 3:
				pool.append((w_len % (limits[1] + 1)) + limits[0])
			else:
				pool.append(w_len)
		if len(pool) > 4:
			return pool
	
	for c in string:
		string_int = abs(ord(c) - ord('a'))
		pool.append((string_int % (limits[1] + 1)) + limits[0])

	return pool

def fill_duration_s(string, target_dur=1, how_many_values=None, grains=None, _index=0):
	"""
	Fills a target duration with a specified number of values using given grains,
	using a string as a deterministic pseudo-random source.

	Args:
		string (str): The string to derive variation from.
		target_dur (float): The total duration to be filled.
		how_many_values (int): The maximum number of values to generate.
		grains (list): A list of possible duration values (grains) to use.
		_index (int): Internal offset index for recursion.

	Returns:
		list: A list of duration values that sum up to the target duration.
	"""

	if how_many_values is None:
		how_many_values = len(string)

	if grains is None:
		grains = [1 / pow(2, x) for x in range(1, 6)]

	print(f'I am filling a duration of {target_dur = } with {how_many_values} values - using {string = } and index {_index}')

	#string_int = [abs(ord(c.lower()) - ord('a')) for c in string if c.isalpha()]
	string_int = [abs(ord(c) - ord('a')) for c in string if c.isalpha()]
	if not string_int:
		raise ValueError("Input string must contain at least one alphabetical character.")

	values = []
	remaining = target_dur
	index_candidate = 0

	while remaining > 0 and len(values) < how_many_values:
		candidates = [v for v in grains if v <= remaining]
		if not candidates:
			break
		idx = (index_candidate + _index) % len(string_int)
		grain_idx = string_int[idx] % len(candidates)
		n = candidates[grain_idx]
		values.append(n)
		remaining = round(remaining - n, 10)
		index_candidate += 1

	if remaining == 0:
		return values
	else:
		return fill_duration_s(string, target_dur, how_many_values, grains, _index=_index + 1)