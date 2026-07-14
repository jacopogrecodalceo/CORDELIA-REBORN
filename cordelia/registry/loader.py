import importlib 
import orjson
import cordelia.path
from cordelia.errors import *

def load_module(path):
	name = path.stem
	spec = importlib.util.spec_from_file_location(name, path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return name, module

def require_callable(module, attr):
	func = getattr(module, attr, None)
	if not callable(func):
		raise CordeliaInitError(f'do not have a {attr} function')
	return func

registry_func = {}
for path in cordelia.path.func_corpus_dir.rglob("*.py"):
	if path.stem.startswith("_"):
		continue
	name, module = load_module(path)
	registry_func[name] = require_callable(module, "main")

registry_quality = {}
for path in cordelia.path.qualities_corpus_dir.rglob("*.py"):
	if path.stem.startswith("_"):
		continue

	quality_name = path.parent.name   	# talea, colores, dur...
	name     = path.stem          		# eu, iam, talea, mode...

	spec   = importlib.util.spec_from_file_location(name, path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)

	if quality_name not in registry_quality:
		registry_quality[quality_name] = {}
	registry_quality[quality_name][name] = {
		'main': require_callable(module, "main"),
		'match': require_callable(module, "match"),
	}
