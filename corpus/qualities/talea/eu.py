from corpus.qualities.talea import *

def match(items: list) -> bool:
	if items[0] == 'eu':
		return True
	return False

@auto_config(Cycle, Talea)
def main(args):
	items = args.quality.items

	args = items[1:]
	if 'in' in args:
		cycle = args[-1]
		args = args[:-2]

	pulses = int(args[0])
	steps = int(args[1])
	
	shift = 0
	if len(args) == 3:
		shift = int(args[2])

	return cycle, _bjorklund(pulses, steps, shift=shift)

def _bjorklund(pulses: int, steps: int, shift: int = 0) -> list[int]:
	if not 0 <= pulses <= steps:
		raise ValueError(f"0 <= pulses ({pulses}) <= steps ({steps}) required")
	
	pattern = [1 if (i * pulses) % steps < pulses else 0 for i in range(steps)]
	
	if shift:
		shift *= -1
		shift %= steps
		pattern = pattern[shift:] + pattern[:shift]
	
	return pattern