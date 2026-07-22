import importlib.util
from pathlib import Path
from typing import Any, Callable

import cordelia.path
from cordelia.errors import CordeliaInitError
from cordelia.models.types import QualityStage


def load_module(path: Path):
	"""Load a single plugin file as a module."""
	name = path.stem
	spec = importlib.util.spec_from_file_location(name, path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return name, module


def require_callable(module, attr: str) -> Callable:
	"""Fetch a mandatory callable. Raises if missing or not callable."""
	func = getattr(module, attr, None)
	if not callable(func):
		raise CordeliaInitError(f"{module.__name__} is missing required function '{attr}'")
	return func


def optional_callable(module, attr: str, default: Any = None) -> Any:
	"""Fetch an optional callable. Returns `default` if the attribute is absent."""
	func = getattr(module, attr, None)
	if func is None:
		return default
	return func


def _iter_plugin_files(directory: Path):
	"""Yield non-private .py files under a corpus directory."""
	for path in directory.rglob("*.py"):
		if not path.stem.startswith("_"):
			yield path


def build_func_registry() -> dict[str, Callable]:
	registry = {}
	for path in _iter_plugin_files(cordelia.path.func_corpus_dir):
		name, module = load_module(path)
		registry[name] = require_callable(module, "main")
	return registry


def build_quality_registry() -> dict[str, dict[str, dict]]:
	registry: dict[str, dict[str, dict]] = {}
	for path in _iter_plugin_files(cordelia.path.qualities_corpus_dir):
		quality_name = path.parent.name   # talea, colores, dur...
		name, module = load_module(path)  # eu, iam, mode...

		registry.setdefault(quality_name, {})[name] = {
			'main': require_callable(module, "main"),
			'match': require_callable(module, "match"),
			'stage': optional_callable(module, "stage", default=QualityStage.PRIMARY),
		}
	return registry


registry_func = build_func_registry()
registry_quality = build_quality_registry()