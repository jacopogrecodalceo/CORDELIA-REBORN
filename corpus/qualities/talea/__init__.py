import importlib
import pkgutil
import inspect

from pathlib import Path

package_dir = Path(__file__).parent

for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
	module = importlib.import_module(f".{module_name}", package=__package__)
	for name, obj in inspect.getmembers(module, inspect.isfunction):
		if not name.startswith("_"):
			globals()[name] = obj
			
