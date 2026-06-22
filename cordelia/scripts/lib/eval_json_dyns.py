"""
Convert dynamic markings from dB to normalized amplitude.
"""
import json
import cordelia.path
from cordelia.helpers import db_to_amplitude



# Or if you have the helper:
# from cordelia.helpers import db_to_amplitude

# Read the JSON file
# Update this path to your actual file location

with open(cordelia.path.json / 'dyns.json', 'r') as f:
    data = json.load(f)

func = 'db_to_amp'
new_dict = {}

for dyn, dicts in data.items():
    db_value = dicts[func]
    new_dict[dyn] = {
        'db_to_amp': db_value,
        'norm': db_to_amplitude(db_value),
    }

# Pretty print the result
print(json.dumps(new_dict, indent=2))

# Also print as a simple mapping
print("\n# Simple mapping:")
simple = {dyn: values['amplitude'] for dyn, values in new_dict.items()}
print(json.dumps(simple, indent=2))