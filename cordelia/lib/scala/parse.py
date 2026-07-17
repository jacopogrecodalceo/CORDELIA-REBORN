"""
[Scala rules](https://www.huygens-fokker.org/scala/scl_format.html) #rules
- The files are human readable ASCII or 8-bit character text-files. 1)
- The file type is .scl.
- There is one scale per file.
- Lines beginning with an exclamation mark are regarded as comments and are to be ignored.
- The first (non comment) line contains a short description of the scale, but long lines are possible and should not give a read error. The description is only one line. If there is no description, there should be an empty line.
- The second line contains the number of notes. This number indicates the number of lines with pitch values that follow. In principle there is no upper limit to this, but it is allowed to reject files exceeding a certain size. *The lower limit is 0*, which is possible since degree 0 of 1/1 is implicit. Spaces before or after the number are allowed.
- After that come the pitch values, each on a separate line, either as a **ratio** or as a value in **cents**. **If the value contains a period, it is a cents value, otherwise a ratio**. Ratios are written with a slash, and only one. Integer values with no period or slash should be regarded as such, for example "2" should be taken as "2/1". Numerators and denominators should be supported to at least 2^31-1 = 2147483647. Anything after a valid pitch value should be ignored. Space or horizontal tab characters are allowed and should be ignored. Negative ratios are meaningless and should give a read error. For a description of cents, go [here](http://www.huygens-fokker.org/docs/measures.html#Ellis).
- **The first note of 1/1 or 0.0 cents is implicit and not in the files.**
- Files for which Scala gives _Error in file format_ are incorrectly formatted. They should give a read error and be rejected.
"""

from fractions import Fraction

def parse_scl(text):
	"""Parse .scl file content into (description, intervals).

	intervals is a list of Fraction/float multipliers over 1/1,
	NOT including the implicit 1/1 itself.
	Ratios are returned as Fraction, cents as float (2 ** (cents / 1200)).
	"""
	lines = [line.rstrip("\n") for line in text.splitlines()]
	non_comment_lines = [line for line in lines if not line.strip().startswith("!")]

	if len(non_comment_lines) < 1:
		raise ValueError("Invalid .scl file: missing description line")

	#description = non_comment_lines[0].strip()

	if len(non_comment_lines) < 2:
		raise ValueError("Invalid .scl file: missing note count line")

	try:
		note_count = int(non_comment_lines[1].strip())
	except ValueError:
		raise ValueError("Invalid .scl file: note count is not an integer")

	if note_count < 0:
		raise ValueError("Invalid .scl file: negative note count")

	pitch_lines = non_comment_lines[2:2 + note_count]
	if len(pitch_lines) < note_count:
		raise ValueError("Invalid .scl file: fewer pitch lines than declared")

	intervals = [parse_pitch(line) for line in pitch_lines]
	return intervals


def parse_pitch(line):
	"""Parse a single pitch line into a Fraction (ratio) or float (cents multiplier)."""
	token = line.strip().split()[0] if line.strip() else ""
	if not token:
		raise ValueError("Invalid .scl file: empty pitch line")

	if "." in token:
		cents = float(token)
		return 2 ** (cents / 1200)

	if "/" in token:
		numerator_str, denominator_str = token.split("/", 1)
		numerator = int(numerator_str)
		denominator = int(denominator_str)
	else:
		numerator = int(token)
		denominator = 1

	if numerator <= 0 or denominator <= 0:
		raise ValueError(f"Invalid .scl file: non-positive ratio '{token}'")

	return Fraction(numerator, denominator)


def get_frequencies(text, origin=440):
	"""Return list of frequencies for the scale, starting with root (1/1)."""
	intervals = parse_scl(text)
	frequencies = [origin]
	for interval in intervals:
		frequencies.append(origin * float(interval))
	return frequencies

def expand_to_range(frequencies, low=20.0, high=20000.0):
	"""Stack the scale up/down by its equave ratio to fill [low, high]."""
	equave_ratio = frequencies[-1] / frequencies[0]

	result = set()

	for base_freq in frequencies:
		freq = base_freq

		while freq >= low:
			if freq <= high:
				result.add(freq)
			freq /= equave_ratio

		freq = base_freq * equave_ratio
		while freq <= high:
			if freq >= low:
				result.add(freq)
			freq *= equave_ratio

	return sorted(result)

if __name__ == "__main__":
	with open("/Users/j/Documents/PROJECTs/CORDELIA-REBORN/corpus/scala/_current/jacques/edo31hex.scl") as file:
		content = file.read()
	intervals = parse_scl(content)
	print(get_frequencies(content, origin=440.0))
	print(expand_to_range(get_frequencies(content, origin=440.0)))