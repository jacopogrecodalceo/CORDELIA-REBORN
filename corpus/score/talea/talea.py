"""
=========================================
talea is a talea function
1. the first arg is always "talea" that's also the main deduction for this function 
2. it is an array but 
	-	rest is 0
	-	negative number is rest x duration (this means that 0 == -1)
3. the time is always at the end after the first "in" if there's no "in" in the last one before. it is automatically set
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
	if items[0] == 'talea':
		return True
	return False

def main(items: list) -> Talea:
	args = items[1:]
	
	# Extract and normalize pulse pattern
	pulses = args[0]
	pulse_values = pulses.items if isinstance(pulses, Array) else [pulses]

	# Default values
	duration = 8  # Default duration in beats
	pad_length = None
	
	# Parse remaining arguments
	i = 1
	while i < len(args):
		if isinstance(args[i], int):
			if i + 1 >= len(args):
				raise ValueError("'pad' requires a length argument")
			pad_length = args[i + 1]
			i += 2
		
		elif args[i] == 'in':
			if i + 1 >= len(args):
				raise ValueError("'in' requires a duration argument")
			duration = args[i + 1]
			i += 2
		
		else:
				# Unknown argument - skip or raise error
				i += 1
	
	# Apply padding if specified
	if pad_length is not None:
		if len(pulse_values) < pad_length:
			# Pad with zeros to reach desired length
			pulse_values = pulse_values + [0] * (pad_length - len(pulse_values))
		else:
			# Truncate if longer than pad length
			pulse_values = pulse_values[:pad_length]
	
	return Talea(values=pulse_values, cycle=duration)