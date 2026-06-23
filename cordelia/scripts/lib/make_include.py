from pathlib import Path
from cordelia.console import console
import cordelia.path

directory = Path(cordelia.path.csound)

includes = []

for path in directory.rglob("*.orc"):
	if 'include' in str(path):
		continue
	includes.append(f'#include "{path}"')

includes.sort()

cordelia.path.include.write_text("\n".join(includes))
console.print(f'File written @{cordelia.path.include}')