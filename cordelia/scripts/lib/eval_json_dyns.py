import json
import cordelia.path
from cordelia.console import console
from cordelia.helpers import db_to_amplitude
# Or if you have the helper:
# from cordelia.helpers import db_to_amplitude

# Read the JSON file
# Update this path to your actual file location

INPUT_DIR = cordelia.path.corpus_json_dir
OUTPUT_JSON = cordelia.path.corpus_json_dir / 'dyn.json'

with open(INPUT_DIR / 'dyn.json', 'r') as f:
    data = json.load(f)

new_dict = {}

for dyn_name, dicts in data.items():
    db_value = dicts['ampdb']
    new_dict[dyn_name] = {
        'ampdb': db_value,
        'norm': str(db_to_amplitude(db_value)),
    }

with open(OUTPUT_JSON, 'w') as f:
	json.dump(new_dict, f, indent=3)

console.print(f'written @{OUTPUT_JSON}')