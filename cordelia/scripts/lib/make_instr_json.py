import json
from pathlib import Path
from cordelia.console import console
import cordelia.path

INPUT_DIR = Path(cordelia.path.corpus / 'instr')
OUTPUT_JSON = cordelia.path.corpus / '_json' / 'instruments.json'  # Changed: use / operator

instrs = {}
for path in INPUT_DIR.rglob("*.orc"):
    name = path.stem
    if name in instrs:
        raise ValueError(f'DUPLICATE NAME IN OPCODE: {name}')
    instrs[name] = str(path)

# Fixed: need to pass the data as second argument
with open(OUTPUT_JSON, 'w') as f:
    json.dump(instrs, f, indent=3)  # Added indent for readability

# Fixed: use the correct path
console.print(f'File written @{OUTPUT_JSON}')