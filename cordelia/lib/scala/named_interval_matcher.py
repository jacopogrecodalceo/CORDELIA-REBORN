# litchi/lib/tuning/named_interval_matcher.py

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
import json
from cordelia.path import intervals_corpus_json

INTERVAL_NAMEs = json.load(intervals_corpus_json)

@dataclass
class NamedIntervalMatch:
	name: str
	interval_name_ratio: str


class IntervalNamer:
	"""
	Resolves a ratio to a named interval (e.g. 5/4 -> "major third").
	The naming table is injected so alternative naming systems (just
	intonation catalogs, historical temperaments, custom Cordelia
	vocabularies...) can be swapped in without touching Interval itself.
	"""

	def __init__(self, table: dict = None, min_tolerance: int = 1, max_tolerance: int = 6):
		self.table = table if table is not None else INTERVAL_NAMEs
		self.min_tolerance = min_tolerance
		self.max_tolerance = max_tolerance

	def match(self, ratio: Fraction) -> NamedIntervalMatch | None:
		exact_key = str(ratio) if ratio != 1 else '1/1'

		for name, entry in self.table.items():
			if str(entry['ratio']) == exact_key:
				return NamedIntervalMatch(name, str(entry['ratio']))

		tolerance = self.max_tolerance
		while tolerance >= self.min_tolerance:
			tolerance_value = Decimal(1) / (Decimal(10) ** tolerance)

			for name, entry in self.table.items():
				if abs(Fraction(entry['ratio']) - ratio) < tolerance_value:
					return NamedIntervalMatch(name, str(entry['ratio']))

			tolerance -= 1

		return None