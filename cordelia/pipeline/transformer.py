from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from lark import Transformer, Token, Tree

# ---------------------------------------------------------------------------- #
#                                    MODELs                                    #
# ---------------------------------------------------------------------------- #

@dataclass
class Instrument:
	name: str
	score: list[Quality] = field(default_factory=list)
	modifiers: list[Modifier] = field(default_factory=list)

@dataclass
class Variable:
	name: str
	value: list[Any] = field(default_factory=list)

# ---------------------------------------------------------------------------- #

@dataclass
class Modifier:
	kind: str        # "dot" | "colon"
	name: str
	array: Array | None = None

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

# ---------------------------------------------------------------------------- #
#                                    ERRORs                                    #
# ---------------------------------------------------------------------------- #

class CordeliaDeductionError(Exception):
	pass

# ---------------------------------------------------------------------------- #
#                                  TRANSFORMER                                 #
# ---------------------------------------------------------------------------- #
class CordeliaTransformer(Transformer):

	# ── atoms / funcs ─────────────────────────────────────────────────────────

	def func(self, children):
		name = str(children[0])
		arr = children[1] if len(children) > 1 else Array()
		return Func(name=name, args=arr.items)

	# ── arrays ────────────────────────────────────────────────────────────────

	def array(self, children):
		return Array(items=list(children))

	paren_array = array
	brace_array = array

	# ── quality / score ───────────────────────────────────────────────────────

	def quality(self, children):
		return Quality(items=list(children))

	def score(self, children):
		return Score(items=list(children))

	# ── header ────────────────────────────────────────────────────────────────

	def header(self, children):
		return str(children[0])

	# ── modifiers ─────────────────────────────────────────────────────────────

	def dot_mod(self, children):
		name = str(children[0])
		arr = children[1] if len(children) > 1 else None
		return Modifier(kind="sequence", name=name, array=arr)

	def colon_mod(self, children):
		name = str(children[0])
		arr = children[1] if len(children) > 1 else None
		return Modifier(kind="parallel", name=name, array=arr)

	def modifier(self, children):
		return children[0]

	# ── statement → Variable ──────────────────────────────────────────────────

	def statement(self, children):
		name = children[0]
		items = list(children[1:])
		return Variable(name=name, value=items)

	# ── phrase → Instrument ───────────────────────────────────────────────────

	def phrase(self, children):
		name = children[0]
		rest = children[1:]
		modifiers = []
		score = None
		for c in rest:
			if isinstance(c, Modifier):
					modifiers.append(c)
			elif isinstance(c, Score):
					if score is not None:
						raise CordeliaDeductionError(f"duplicate score in phrase '{name}'")
					score = c
			else:
					raise CordeliaDeductionError(f"unexpected child in phrase '{name}': {c!r}")
		if score is None:
			raise CordeliaDeductionError(f"phrase '{name}' has no score")
		return Instrument(name=name, score=score.items, modifiers=modifiers)

	# ── unit ──────────────────────────────────────────────────────────────────

	def unit(self, children):
		return children[0]
