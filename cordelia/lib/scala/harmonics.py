# litchi/lib/tuning/harmonics.py

"""Harmonic-series utilities, independent of any particular Scale."""

from decimal import Decimal


def calculate_harmonics(freq, n: int = 32) -> list:
	return [freq * i for i in range(n)]


def find_nearest_harmonics(harmonics1: list, harmonics2: list):
	harmonics1 = sorted(harmonics1)
	harmonics2 = sorted(harmonics2)

	min_diff = float('inf')
	nearest_pair = (None, None)

	i, j = 1, 1
	while i < len(harmonics1) and j < len(harmonics2):
		diff = abs(Decimal(harmonics1[i]) - harmonics2[j])
		if diff < min_diff:
			min_diff = diff
			nearest_pair = (i, harmonics1[i], harmonics2[j])

		if harmonics1[i] < harmonics2[j]:
			i += 1
		else:
			j += 1

	return nearest_pair, min_diff