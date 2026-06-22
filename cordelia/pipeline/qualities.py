"""
qualities.py — plugin loader for corpus/qualities
===================================================

ROLE IN THE PIPELINE
--------------------
scans corpus/qualities/** for .py plugin files,
loads each one and registers it in deduction.py.

   startup
      ↓
   qualities.py    ← you are here
      ↓
   deduction._registry populated
      ↓
   deduce_quality() ready to use
"""

import importlib.util
from loguru import logger

import cordelia.path
from cordelia.pipeline.deduction import register

_registry: dict[str, dict] = {}

def load():
   """scan and load all quality plugins from corpus/qualities"""
   for path in cordelia.path.qualities.rglob("*.py"):
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


def get(category: str, name: str):
   """get a plugin module by category and name"""
   return _registry.get(category, {}).get(name)


def call(category: str, name: str, *args, **kwargs):
   """call the main function of a plugin — assumes func has same name as file"""
   module = get(category, name)
   if not module:
      raise ValueError(f"plugin not found: {category}/{name}")
   func = getattr(module, name, None)
   if not func:
      raise ValueError(f"no function '{name}' in {category}/{name}.py")
   return func(*args, **kwargs)

