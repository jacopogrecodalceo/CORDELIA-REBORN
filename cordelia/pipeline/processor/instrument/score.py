from __future__ import annotations
import importlib
from typing import Any
from loguru import logger

import cordelia.path
from cordelia.models.transformers import Quality, Instrument
from cordelia.models.score import *


class CordeliaDeductionError(Exception):
   pass

# ─── REGISTRY ────────────────────────────────────────────────────────────────
# populated by the plugin loader in cordelia/pipeline/qualities.py
# each entry is a module with match() and a main function named after the file

_registry: dict[str, dict[str, Any]] = {}
logger.debug(_registry)


def register(category: str, name: str, module: Any):
   """register a plugin module under its category and name"""
   if category not in _registry:
      _registry[category] = {}
   _registry[category][name] = module
   
def load():
   for path in cordelia.path.score.rglob("*.py"):
      if path.stem.startswith("_"):
         continue

      category = path.parent.name   # talea, colores, dur...
      name     = path.stem          # eu, iam, talea, mode...

      spec   = importlib.util.spec_from_file_location(name, path)
      module = importlib.util.module_from_spec(spec)
      spec.loader.exec_module(module)

      if category not in _registry:
         _registry[category] = {}
      _registry[category][name] = module

      register(category, name, module)
      logger.debug(f"SCORE | loaded {category}/{name}")

   for k, v in _registry.items():
      logger.debug(f"SCORE | registry: {k}: {list(v.keys())}")



# ─── DEDUCTION ───────────────────────────────────────────────────────────────

def deduce_quality(quality: Quality, instrument: Instrument):
   for category, plugins in _registry.items():
      for name, module in plugins.items():
         logger.debug(f"deducing {quality.items} for category {category}, file {name}")
         if module.match(quality.items):
            fn = getattr(module, 'main', None)
            if fn is None:
               raise CordeliaDeductionError(
                  f"plugin {category}/{name} has no function '{name}'"
               )
            return fn(quality, instrument)

   raise CordeliaDeductionError(
      f"no plugin matched quality: {quality.items}"
   )
