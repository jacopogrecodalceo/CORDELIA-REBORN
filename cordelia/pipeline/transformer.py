from lark import Transformer
from cordelia.models.ast import *
from cordelia.pipeline.expander import expand
# ---------------------------------------------------------------------------- #
#                                    ERRORs                                    #
# ---------------------------------------------------------------------------- #

class CordeliaDeductionError(Exception):
	pass

# ---------------------------------------------------------------------------- #
#                                  TRANSFORMER                                 #
# ---------------------------------------------------------------------------- #
class CordeliaTransformer(Transformer):

	# ---------------------------------------------------------------------------- #
	#                                    TOKENs                                    #
	# ---------------------------------------------------------------------------- #
	def NAME(self, token):
		return str(token)

	def NOTE(self, token):
		return str(token)

	def SYM(self, token):
		return str(token)

	def DEGREE(self, token):
		return str(token)

	def REPEAT(self, token):
		return str(token)

	def NUMBER(self, token):
		return str(token)

	def ALEA(self, token):
		return str(token)

	# ---------------------------------------------------------------------------- #
	#                                     RULEs                                    #
	# ---------------------------------------------------------------------------- #

	def func(self, children):
		name = str(children[0])
		items = children[1]
		return Func(name=name, args=expand(items))

	def array(self, children):
		items = list(children)
		return expand(items)

	# ── quality / score ───────────────────────────────────────────────────────

	def quality(self, children):
		items = list(children)
		return Quality(items=expand(items))

	def score(self, children):
		return PreScore(items=list(children))

	# ── header ────────────────────────────────────────────────────────────────

	def header(self, children):
		if len(children) > 1:
			return str(children[0]), int(children[1])
		return str(children[0]), 1

	# ── modifiers ─────────────────────────────────────────────────────────────

	def serial(self, children):
		name = str(children[0])
		array = children[1] if len(children) > 1 else None
		if array:
			array = expand(array)
		return Modifier(kind="serial", name=name, values=array)

	def parallel(self, children):
		name = str(children[0])
		array = children[1] if len(children) > 1 else None
		if array:
			array = expand(array)  
		return Modifier(kind="parallel", name=name, values=array)

	def modifier(self, children):
		return children[0]

	# ---------------------------------------------------------------------------- #
	#                                 MAIN CLASSEs                                 #
	# ---------------------------------------------------------------------------- #

	def statement(self, children):
		name = children[0]
		items = list(children[1:])
		return Variable(name=name, value=expand(items))

	def phrase(self, children):
		name, name_id = children[0] # header
		rest = children[1:]
		modifiers = []
		score = None
		for c in rest:
			if isinstance(c, Modifier):
					modifiers.append(c)
			elif isinstance(c, PreScore):
					if score is not None:
						raise CordeliaDeductionError(f"duplicate score in phrase '{name}'")
					score = c
			else:
					raise CordeliaDeductionError(f"unexpected child in phrase '{name}': {c!r}")
		if score is None:
			raise CordeliaDeductionError(f"phrase '{name}' has no score")
		return Instrument(name=name, qualities=score.items, modifiers=modifiers, name_id=name_id)

_transformer = CordeliaTransformer()
def transform(chunks: list) -> list:
   return [_transformer.transform(chunk) for chunk in chunks]
