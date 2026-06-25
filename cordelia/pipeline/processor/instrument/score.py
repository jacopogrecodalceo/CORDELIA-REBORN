from __future__ import annotations
import importlib
from typing import Any
from loguru import logger

import cordelia.path
from cordelia.models.transformers import Quality
from cordelia.models.score import *

""" 
def get(category: str, name: str):
   return _registry.get(category, {}).get(name)

def call(category: str, name: str, *args, **kwargs):
   module = get(category, name)
   if not module:
      raise ValueError(f"plugin not found: {category}/{name}")
   func = getattr(module, name, None)
   if not func:
      raise ValueError(f"no function '{name}' in {category}/{name}.py")
   return func(*args, **kwargs)


def deduce_quality(quality: Quality):
   for fn in _registry:
      result = fn(quality)
      if result is not None:
         return result
   raise CordeliaDeductionError(
      f"Cannot deduce quality from {quality.items!r}"
   )

 """
"""
deduction.py — quality deduction registry
==========================================

ROLE IN THE PIPELINE
--------------------
receives a Quality (list of raw items from the transformer)
and dispatches to the right plugin function by calling each
plugin's match() until one returns True.

   transformer.py
         ↓
   deduction.py    ← you are here
         ↓
   corpus/qualities/talea/eu.py
   corpus/qualities/colores/mode.py
"""


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
      logger.debug(f"qualities | loaded {category}/{name}")

   logger.debug(f"qualities | registry: {list(_registry.keys())}")



# ─── DEDUCTION ───────────────────────────────────────────────────────────────

def deduce_quality(quality: Quality) -> Talea | Colores | Dur | Dyn | Env | Space | Character:
   for category, plugins in _registry.items():
      for name, module in plugins.items():
         if module.match(quality.items):
            print(name, module)
            fn = getattr(module, 'main', None)
            if fn is None:
               raise CordeliaDeductionError(
                  f"plugin {category}/{name} has no function '{name}'"
               )
            return fn(quality.items)

   raise CordeliaDeductionError(
      f"no plugin matched quality: {quality.items}"
   )