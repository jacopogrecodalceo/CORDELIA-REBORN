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
   ...
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from loguru import logger

from cordelia.pipeline.quality_models import *

# ─── MODELS ──────────────────────────────────────────────────────────────────

@dataclass
class Quality:
   items: list[Any] = field(default_factory=list)


# ─── ERRORS ──────────────────────────────────────────────────────────────────

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


# ─── DEDUCTION ───────────────────────────────────────────────────────────────

def deduce_quality(quality: Quality) -> Talea | Colores | Dur | Dyn | Env | Space:
   """
   iterate all registered plugins and call the first one whose match()
   returns True.

   args:
      quality: a Quality with a list of raw items from the transformer

   returns:
      (category/name, result) where result is a typed model dataclass

   raises:
      CordeliaDeductionError if no plugin matches
   """
   for category, plugins in _registry.items():
      for name, module in plugins.items():
         if module.match(quality.items):
            fn = getattr(module, name, None)
            if fn is None:
               raise CordeliaDeductionError(
                  f"plugin {category}/{name} has no function '{name}'"
               )
            return fn(quality.items)

   raise CordeliaDeductionError(
      f"no plugin matched quality: {quality.items}"
   )