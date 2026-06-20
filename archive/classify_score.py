import orjson
from pathlib import Path
import re
from collections import defaultdict

path = Path("/Users/j/Documents/PROJECTs/cordelia_new/data/_json")
score = ".dpf()\n:del()\n:radio()\ntalea 3, 4 d#4 1 3# 4 pto_diat"
score_words = set(re.findall(r'[a-zA-Z_]+', score))

class IndexedData:
	def __init__(self, path):
		self._path = path
		self._data = {}
		self._key_index = defaultdict(list)  # key -> list of (filename, value)
		
		# Load all data and build index
		for file_path in self._path.glob("*.json"):
				filename = file_path.stem
				with open(file_path, 'rb') as f:
					file_data = orjson.loads(f.read())
					self._data[filename] = file_data
					# Index every key
					for key, value in file_data.items():
						self._key_index[key].append((filename, value))
	
	def has_key(self, key):
		return key in self._key_index
	
	def get(self, key):
		if key in self._key_index:
				return self._key_index[key]  # Returns list of (filename, value)
		return None

# Initialize once at startup (takes ~2-3 seconds for 20MB)
data = IndexedData(path)

# During live coding - instant lookups
found_keys = {key for key in score_words if data.has_key(key)}

# Get values for found keys
for key in found_keys:
	matches = data.get(key)
	print(f"'{key}' found in:")
	for kind, value in matches:
		print(f"  {kind}.{key} = {value}")
		