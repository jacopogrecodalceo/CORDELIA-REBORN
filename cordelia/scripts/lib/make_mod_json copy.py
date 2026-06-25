import json
from pathlib import Path
from cordelia.console import console
import cordelia.path

INPUT_DIR = Path(cordelia.path.corpus / 'mod')
OUTPUT_JSON = cordelia.path.corpus / '_json' / 'mods.json'  # Changed: use / operator

mods = {}
for path in INPUT_DIR.rglob("*.orc"):
    name = path.stem
    if name in mods:
        raise ValueError(f'DUPLICATE NAME IN OPCODE: {name}')
    mods[name] = str(path)

# Fixed: need to pass the data as second argument
with open(OUTPUT_JSON, 'w') as f:
    json.dump(mods, f, indent=3)  # Added indent for readability

# Fixed: use the correct path
console.print(f'File written @{OUTPUT_JSON}')