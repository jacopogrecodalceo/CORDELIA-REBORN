# litchi/lib/tuning/scale_builders.py

"""
Pluggable scale construction strategies.

Each builder takes whatever parameters it needs and returns a list of
raw interval values (Decimal or float), NOT including the implicit 1/1
origin - Scale.make() handles inserting that. New construction
strategies (harmonic-series subsets, historical temperaments, imported
tuning files...) can be added here and wired into the registry without
touching Scale itself.
"""

from decimal import Decimal
from fractions import Fraction

from cordelia.registry import data

def build_edo(n: int) -> list:
	"""Equal division of the octave into n steps."""
	return [Decimal(2) ** (Decimal(step) / Decimal(n)) for step in range(n)]


def build_edo_linear(n: int) -> list:
	"""Linear (arithmetic, not geometric) division of the octave into n steps."""
	return [Decimal(1) + (Decimal(step) / Decimal(n)) for step in range(n)]


def build_from_scala_database(scala_name: str) -> list:
	"""Loads a named scale from the bundled Scala (.scl) database."""
	raw_values = data['scala'][scala_name]['tuning_values'].strip().split(',')
	values = [Decimal(x) if '/' not in x else float(Fraction(x)) for x in raw_values]
	if values and values[-1] == 2:
		values.pop(-1)
	return values


SCALE_BUILDERs = {
	'edo': build_edo,
	'edolin': build_edo_linear,
	'scala': build_from_scala_database,
}