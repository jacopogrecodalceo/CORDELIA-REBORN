from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from lark import Transformer, Token, Tree

@dataclass
class Instrument:
	name: str
	score: list[Quality] = field(default_factory=list)
	modifiers: list[Modifier] = field(default_factory=list)
	id: int = field(default_factory=1)

@dataclass
class Variable:
	name: str
	value: list[Any] = field(default_factory=list)

# ---------------------------------------------------------------------------- #

@dataclass
class Modifier:
	kind: str        # "dot" | "colon"
	name: str
	args: Array | None = None

@dataclass
class Score:
   items: list[Quality] = field(default_factory=list)

# ---------------------------------------------------------------------------- #

@dataclass
class Quality:
   items: list[Any] = field(default_factory=list)

@dataclass
class Func:
	name: str
	args: list[Any] = field(default_factory=list)

@dataclass
class Array:
	items: list[Any] = field(default_factory=list)
