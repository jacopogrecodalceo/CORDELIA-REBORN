from corpus.qualities.talea import *

def match(items: list) -> bool:
	if items[0] == 'eu':
		return True
	return False

@auto_config('cycle', 'talea')
def main(args):
	items = args.quality.items

	items = items[1:]
	if 'in' in items:
		cycle = items[-1]
		items = items[:-2]

	shift = 0
	match len(items):
		case 1:
			pulses = int(items[0])
			steps = int(items[0])
		case 2:
			pulses = int(items[0])
			steps = int(items[1])
		case 3:
			pulses = int(items[0])
			steps = int(items[1])
			shift = int(items[2])

	if pulses > steps:
		pulses = steps

	return cycle, bjorklund_shift(pulses, steps, shift=shift)

def _bjorklund(pulses: int, steps: int) -> list[int]:
	if pulses == 0:
		return [0] * steps

	front = [[1] for _ in range(pulses)]
	back = [[0] for _ in range(steps - pulses)]

	while len(back) > 1:
		pair_count = min(len(front), len(back))
		new_front = [front[i] + back[i] for i in range(pair_count)]
		new_back = front[pair_count:] if len(front) > pair_count else back[pair_count:]
		front, back = new_front, new_back

	return [x for group in front + back for x in group]

def bjorklund_shift(pulses: int, steps: int, shift: int = 0) -> list[int]:
	pattern = _bjorklund(pulses, steps)
	if shift:
		shift %= steps
		pattern = pattern[-shift:] + pattern[:-shift]
	return pattern