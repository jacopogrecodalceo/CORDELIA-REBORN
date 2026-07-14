from pathlib import Path
import orjson
import re

path = Path('/Users/j/Documents/PROJECTs/CORDELIA/cordelia/config')


for f in path.glob("*.json"):
	data = orjson.loads(f.read_bytes())
	print(f"\nProcessing: {f.name}")
	if f.stem not in ['tokens']:
		for k in data:
			if re.compile(r'x\d+$').search(k):  # or pattern.match(k) if you want from start
				print(f"\t ··· X NUM {k}")
			elif re.compile(r'x$').search(k): 
				print(f"\t ··· X     {k}")
