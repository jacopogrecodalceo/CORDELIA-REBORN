from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from lark import Transformer, Token, Tree
from cordelia.pipeline.deduction import Quality, deduce_quality

# ─── ERRORS ──────────────────────────────────────────────────────────────────

class CordeliaDeductionError(Exception):
	pass


# ─── MODELS ──────────────────────────────────────────────────────────────────

@dataclass
class Func:
	name: str
	args: list[Any] = field(default_factory=list)


@dataclass
class Array:
	items: list[Any] = field(default_factory=list)


@dataclass
class Mod:
	kind: str        # "dot" | "colon"
	name: str
	array: Array | None = None

@dataclass
class Score:
	qualities: list[Quality] = field(default_factory=list)


@dataclass
class Instrument:
	name: str
	qualities: dict[str, Quality] = field(default_factory=dict)
	modifiers: list[Mod] = field(default_factory=list)


@dataclass
class Variable:
	name: str
	items: list[Any] = field(default_factory=list)


# ─── TRANSFORMER ─────────────────────────────────────────────────────────────

class CordeliaTransformer(Transformer):

	# ── atoms / funcs ─────────────────────────────────────────────────────────

	def atom(self, children):
		c = children[0]
		if isinstance(c, Array):
			return c
		return str(c)

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
		return Score(qualities=list(children))

	# ── header ────────────────────────────────────────────────────────────────

	def header(self, children):
		return str(children[0])

	# ── modifiers ─────────────────────────────────────────────────────────────

	def dot_mod(self, children):
		name = str(children[0])
		arr = children[1] if len(children) > 1 else None
		return Mod(kind="dot", name=name, array=arr)

	def colon_mod(self, children):
		name = str(children[0])
		arr = children[1] if len(children) > 1 else None
		return Mod(kind="colon", name=name, array=arr)

	def modifier(self, children):
		return children[0]

	# ── statement → Variable ──────────────────────────────────────────────────

	def statement(self, children):
		name = children[0]
		items = list(children[1:])
		return Variable(name=name, items=items)

	# ── phrase → Instrument ───────────────────────────────────────────────────

	def phrase(self, children):
		name = children[0]
		modifiers = [c for c in children[1:] if isinstance(c, Mod)]
		score = next((c for c in children[1:] if isinstance(c, Score)), Score())
		print(name, modifiers, score)
		qualities = {}
		for q in score.qualities:
			# a quality.items is a list[Any]
			key, val = deduce_quality(q)
			qualities[key] = val

		return Instrument(name=name, qualities=qualities, modifiers=modifiers)

	# ── unit ──────────────────────────────────────────────────────────────────

	def unit(self, children):
		return children[0]