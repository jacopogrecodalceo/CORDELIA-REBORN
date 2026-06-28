from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from lark import Transformer, Token, Tree

from enum import Enum

class State(Enum):
	BORN = "born"
	SKIP = "skip"
	PATCH = "patch"
	DEAD = "dead"

@dataclass
class Instrument:
	name: str
	qualities: list[Quality]
	modifiers: list[Modifier]
	instr_id: int = field(default_factory=1)
	score: dict = field(default_factory=lambda: {
		'talea': [],
		'colores': [1],
		'dur': [1],
		'dyn': ['mf'],
		'env': ['cls'],
		'space': [0],
		'character': []
	})

	state: State = State.BORN
	cycle: int = 8


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
	"""
	this will always be used during the transoformer phase
	"""
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
