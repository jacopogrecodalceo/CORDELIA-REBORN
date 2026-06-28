from cordelia.pipeline.visitor import visit_list
from cordelia.models.transformers import *

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
	""" def atom(self, children):
		c = children[0]
		if isinstance(c, Array):
			return c
		if c.startswith('x'):
			print('-'*32)
			print(c)
			print('-'*32)
		return str(c) """

	def atom(self, children):
		c = children[0]
		if isinstance(c, Array):
			return c
		return str(c)

	def func(self, children):
		name = str(children[0])
		arr = children[1] if len(children) > 1 else Array()
		items = visit_list(arr.items)
		return Func(name=name, args=items)

	# ── arrays ────────────────────────────────────────────────────────────────

	def array(self, children):
		items = visit_list(list(children))
		return Array(items=items)

	paren_array = array
	brace_array = array

	# ── quality / score ───────────────────────────────────────────────────────

	def quality(self, children):
		items = visit_list(list(children))
		return Quality(items=items)

	def score(self, children):
		return Score(items=list(children))

	# ── header ────────────────────────────────────────────────────────────────

	def id(self, children):
		return int(children[0])

	def header(self, children):
		if len(children) > 1:
			return str(children[0]), children[1]
		return str(children[0]), 1

	# ── modifiers ─────────────────────────────────────────────────────────────

	def dot_mod(self, children):
		name = str(children[0])
		arr = children[1] if len(children) > 1 else None
		return Modifier(kind="sequence", name=name, args=arr)

	def colon_mod(self, children):
		name = str(children[0])
		arr = children[1] if len(children) > 1 else None
		return Modifier(kind="parallel", name=name, args=arr)

	def modifier(self, children):
		return children[0]

	# ── statement → Variable ──────────────────────────────────────────────────

	def statement(self, children):
		name = children[0]
		items = list(children[1:])
		visit_listed_items = visit_list(items)
		return Variable(name=name, value=visit_listed_items)

	# ── phrase → Instrument ───────────────────────────────────────────────────

	def phrase(self, children):
		name, instr_id = children[0]
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
		return Instrument(name=name, qualities=score.items, modifiers=modifiers, instr_id=instr_id)
