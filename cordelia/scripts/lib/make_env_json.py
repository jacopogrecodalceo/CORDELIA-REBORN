import json
import cordelia.path

from cordelia.console import console

INPUT_DIR = cordelia.path.env_corpus_dir
OUTPUT_JSON = cordelia.path.env_corpus_json


ENVs = {}

def add(kind):
	for path in INPUT_DIR.rglob(f"*.{kind}"):
		name = path.stem
		if name in ENVs:
			raise ValueError(f'DUPLICATE NAME: {name}')
		ENVs[name] = {
			'kind': kind,
			'path': str(path)
		}

def make_json():
	# Fixed: need to pass the data as second argument
	with open(OUTPUT_JSON, 'w') as f:
		json.dump(ENVs, f, indent=3)  # Added indent for readability

add('orc')
add('wav')
make_json()

# Fixed: use the correct path
console.print(f'written @{OUTPUT_JSON}')