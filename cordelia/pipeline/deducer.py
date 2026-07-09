from dataclasses import dataclass
import importlib
from typing import Any
from loguru import logger

import cordelia.path

class CordeliaDeductionError(Exception):
	pass

# ─── REGISTRY ────────────────────────────────────────────────────────────────
# populated by the plugin loader in cordelia/pipeline/qualities.py
# each entry is a module with match() and a main function named after the file

quality_registry: dict[str, dict[str, Any]] = {}
func_registry: dict[str, dict[str, Any]] = {}
logger.debug(quality_registry)

def register(category: str, name: str, module: Any):
	"""register a plugin module under its category and name"""
	if category not in quality_registry:
		quality_registry[category] = {}
	quality_registry[category][name] = module
	
def load_qualities_from_corpus():
	for path in cordelia.path.score_corpus_dir.rglob("*.py"):
		if path.stem.startswith("_"):
			continue

		category = path.parent.name   # talea, colores, dur...
		name     = path.stem          # eu, iam, talea, mode...

		spec   = importlib.util.spec_from_file_location(name, path)
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)

		if category not in quality_registry:
			quality_registry[category] = {}
		quality_registry[category][name] = module

		register(category, name, module)
		logger.debug(f"SCORE | loaded {category}/{name}")

	for k, v in quality_registry.items():
		logger.debug(f"SCORE | registry: {k}: {list(v.keys())}")

def load_functions_from_corpus():
	for path in cordelia.path.func_corpus_dir.rglob("*.py"):
		if path.stem.startswith("_"):
			continue
		name   = path.stem
		spec   = importlib.util.spec_from_file_location(name, path)
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)

		func = getattr(module, "main", None)
		if not callable(func):
			continue

		func_registry[name] = func


def load_from_corpus():
	load_qualities_from_corpus()
	load_functions_from_corpus()
 
# ─── DEDUCTION ───────────────────────────────────────────────────────────────
@dataclass
class Argument:
	instrument: type
	quality: type

def deduce_quality(quality, instrument):
	for category, plugins in quality_registry.items():
		for name, module in plugins.items():
			logger.debug(f"deducing {quality.items} for category {category}, file {name}")
			if module.match(quality.items):
				fn = getattr(module, 'main', None)
				if fn is None:
					raise CordeliaDeductionError(
						f"plugin {category}/{name} has no function '{name}'"
					)
				fn(Argument(instrument, quality))
				return True
	raise CordeliaDeductionError(
		f"no plugin matched quality: {quality.items}"
	)

def deduce_function(quality, instrument):
	for category, plugins in quality_registry.items():
		for name, module in plugins.items():
			logger.debug(f"deducing {quality.items} for category {category}, file {name}")
			if module.match(quality.items):
				fn = getattr(module, 'main', None)
				if fn is None:
					raise CordeliaDeductionError(
						f"plugin {category}/{name} has no function '{name}'"
					)
				fn(Argument(instrument, quality))
				return True
	raise CordeliaDeductionError(
		f"no plugin matched quality: {quality.items}"
	)
