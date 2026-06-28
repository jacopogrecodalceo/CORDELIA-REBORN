"""
eu.py — euclidean rhythm quality plugin
=========================================

MATCHES
-------
	eu 3 8        → explicit keyword
	3 8           → two integers, inferred as euclidean

RETURNS
-------
	Talea(pattern=[1,0,0,1,0,0,1,0], cycle=8)
"""
from corpus.score.talea import *

def match(items: list) -> bool:
	if items[0] == 'eu':
		return True
	return False

def main(quality: Quality, instrument: Instrument):
	items = quality.items

	args = items[1:]
	if 'in' in args:
		instrument.cycle = int(args[-1])
		args = args[:-2]

	pulses = int(args[0])
	steps = int(args[1])
	
	shift = 0
	if len(args) == 3:
		shift = int(args[2])

	instrument.score['talea'] = _bjorklund(pulses, steps, shift=shift)

# ─── internal ────────────────────────────────────────────────────────────────

def _is_int(val) -> bool:
	try:
		int(str(val))
		return True
	except ValueError:
		return False


def _bjorklund(pulses: int, steps: int, shift: int = 0) -> list[int]:
	if not 0 <= pulses <= steps:
		raise ValueError(f"0 <= pulses ({pulses}) <= steps ({steps}) required")
	
	pattern = [1 if (i * pulses) % steps < pulses else 0 for i in range(steps)]
	
	if shift:
		shift *= -1
		shift %= steps
		pattern = pattern[shift:] + pattern[:shift]
	
	return pattern