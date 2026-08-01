import re
from decimal import Decimal
import numpy as np
from corpus.qualities.dyn import *
from cordelia.registry.data import data

def match(items: list) -> bool:
	if items[0] in data['dyn']:
		return True
	return False

@auto_config('dyn')
def main(args):
	items = args.quality.items
	if 'in' in items:
		length = items[-1]
		items = items[:-2]
	else:
		length = 8

	items = flatten_items(items)
	return parse_curve(items, length)

def flatten_items(items):
	tokens = []
	for item in items:
		if ('<' in item or '>' in item):
			parts = [p for p in re.split(r'([<>])', item) if p != '']
			tokens.extend(parts)
		else:
			tokens.append(item)
	return tokens

def resolve_norm(name):
	return Decimal(data['dyn'][name]['norm'])

def decimal_linspace(start, stop, num):
	if num == 1:
		return [start]
	step = (stop - start) / Decimal(num - 1)
	return [start + step * Decimal(i) for i in range(num)]

def parse_curve(items, length):
	if '<' in items:
		indicator_index = items.index('<')
	elif '>' in items:
		indicator_index = items.index('>')
	else:
		return items

	prev = items[indicator_index - 1]
	forward = items[indicator_index + 1]

	prev_norm = resolve_norm(prev)
	forward_norm = resolve_norm(forward)

	if prev_norm is None:
		prev_norm = forward_norm
	if forward_norm is None:
		forward_norm = prev_norm

	segment = decimal_linspace(prev_norm, forward_norm, int(length))

	remaining = items[:indicator_index - 1] + [forward] + items[indicator_index + 2:]
	rest = parse_curve(remaining, length)

	return segment + rest[1:]