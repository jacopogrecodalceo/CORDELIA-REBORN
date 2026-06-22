from __future__ import annotations
from lark import Transformer, Token, Tree
from cordelia.pipeline.transformer_models import *
from cordelia.pipeline.deduction import deduce_quality

# ─── ERRORS ──────────────────────────────────────────────────────────────────

class CordeliaDeductionError(Exception):
	pass

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
		return Variable(name=name, value=items)

	# ── phrase → Instrument ───────────────────────────────────────────────────

	def phrase(self, children):
		name = children[0]
		modifiers = [c for c in children[1:] if isinstance(c, Mod)]
		score = next((c for c in children[1:] if isinstance(c, Score)), Score())
		print(name, modifiers, score)
		"""
  		OK so you need a rule-based dispatcher where each quality function registers its own matching condition. 
  		This is the classic chain of responsibility pattern.
 		"""
		return Instrument(name=name, qualities=[deduce_quality(q) for q in score.qualities], modifiers=modifiers)

	# ── unit ──────────────────────────────────────────────────────────────────

	def unit(self, children):
		return children[0]