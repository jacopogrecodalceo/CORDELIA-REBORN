from fractions import Fraction
from corpus.qualities.talea import *

def match(items: list) -> bool:
	if items[0] == 'grov':
		return True
	return False

#@auto_config(Talea)
def main(args):
	items = args.quality.items[1:]
	#UNRESOLVED: [QualityEntry(deduced=[1, 0, 1, 1, 1, 1, 1, 1], raws=['eu', '7', '8', 'in', '2'])] ['grov', '1']
	prev_talea = args.instrument.qualities['talea'].entries[-1].deduced
	args.instrument.qualities['talea'].entries[-1].deduced = list(expand(prev_talea, grooves=[float(Fraction(i)) for i in items]))

def expand(pattern, grooves, target_length=64):
	"""
	Expand binary pattern to target length by stretching each value into a block.
	Groove shifts the position of 1s within their blocks.
	
	Args:
		pattern: list of 0s and 1s e.g. [1, 0, 1, 0]
		target_length: total output length (default 512)
		groove: -1 to 1, shifts 1s earlier (negative) or later (positive)
	
	Returns:
		list of 0s and 1s of length target_length
	"""
	pattern_len = len(pattern)
	
	# Size of each block
	block_size = target_length // pattern_len
	remainder = target_length % pattern_len
	
	result = []
	len_grooves = len(grooves)
	index = 0
	for i, val in enumerate(pattern):
		# Calculate block size (distribute remainder to first few blocks)
		current_block_size = block_size + (1 if i < remainder else 0)

		if val == 1:
				if index == 0:
					index += 1
					continue
				groove = grooves[index%len_grooves]
				# Position of the 1 within the block
				# groove=-1: 1 at the start of the block (rushed)
				# groove=0: 1 in the middle of the block (straight)
				# groove=1: 1 at the end of the block (laid back)
				
				# Calculate position based on groove
				if groove == 0:
					pos = current_block_size // 2  # middle
				elif groove < 0:
					# Shift towards beginning
					shift = abs(groove) * (current_block_size // 2)
					pos = max(0, int(current_block_size // 2 - shift))
				else:  # groove > 0
					# Shift towards end
					shift = groove * (current_block_size // 2)
					pos = min(current_block_size - 1, int(current_block_size // 2 + shift))
				
				# Create block with 1 at calculated position
				block = [0] * current_block_size
				block[pos] = 1
				result.extend(block)
				index += 1
		else:
				# All zeros block
				result.extend([0] * current_block_size)
	
	# Trim or pad to exact target length
	if len(result) > target_length:
		result = result[:target_length]
	elif len(result) < target_length:
		result.extend([0] * (target_length - len(result)))
	
	return result

