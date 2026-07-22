from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class Func:
	"""Function definition with name and items."""
	name: str
	items: list = field(default_factory=list)

@dataclass(frozen=True, slots=True)
class Expr:
	"""Expression container."""
	items: list = field(default_factory=list)

@dataclass(slots=True)
class Verse:
	"""Expression container."""
	items: list = field(default_factory=list)
