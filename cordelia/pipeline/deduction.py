from __future__ import annotations
from typing import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Quality:
   items: list[Any] = field(default_factory=list)

# ─── ERRORS ──────────────────────────────────────────────────────────────────

class CordeliaDeductionError(Exception):
   pass


# ─── REGISTRY ────────────────────────────────────────────────────────────────

_registry: list[Callable[[Quality], tuple[str, Quality] | None]] = []


def deducer(fn: Callable[[Quality], tuple[str, Quality] | None]):
   _registry.append(fn)
   return fn


def deduce_quality(quality: Quality) -> tuple[str, Quality]:
   for fn in _registry:
      result = fn(quality)
      if result is not None:
         return result
   raise CordeliaDeductionError(
      f"Cannot deduce quality from {quality.items!r}"
   )


