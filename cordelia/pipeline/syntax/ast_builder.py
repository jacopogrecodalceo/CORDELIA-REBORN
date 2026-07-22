from lark import Transformer

from cordelia.models.nodes import *
from cordelia.models.ast import *

from cordelia.pipeline.syntax.macro_expander import MacroExpander

from cordelia.errors import *


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

	def MODIFIER_KIND(self, token):
		# children[0] is a Token holding the literal "." or ":"
		symbol = str(token)
		return "serial" if symbol == "." else "parallel"

	# ---------------------------------------------------------------------------- #
	#                                     RULEs                                    #
	#   contract: only rules that ASSEMBLE a fresh list from qualities children call     #
	#   expand(). every other rule trusts its children unchanged. expr never       #
	#   returns a bare list -- single term passes through, multi-term becomes an   #
	#   Expr node, so expand() can never mistake an infix chain for an array.      #
	# ---------------------------------------------------------------------------- #
	def func(self, children):
		name = str(children[0])
		items = children[1]
		return Func(name=name, items=items)

	def expr(self, children):
		return Expr(items=list(children))

	def array(self, children):
		items = list(children)
		return items

	# ---------------------------------------------------------------------------- #
	#                                   QUALITIEs                                  #
	# ---------------------------------------------------------------------------- #

	def verse(self, children):
		items = list(children)
		return Verse(items=items)

	# ---------------------------------------------------------------------------- #
	#                                   header                                   #
	# ---------------------------------------------------------------------------- #

	def header(self, children):
		# children: [NAME] or [NAME, voice_id]
		name = str(children[0])
		if len(children) > 1:
			return Identity(name=name, voice_id=int(children[1]))
		return Identity(name=name)


	# ---------------------------------------------------------------------------- #
	#                                   MODIFIERs                                  #
	# ---------------------------------------------------------------------------- #

	def modifier(self, children):
		kind = children[0]
		name = str(children[1])
		array = children[2] if len(children) > 2 else None
		return Modifier(kind=kind, name=name, items=array)

	# ---------------------------------------------------------------------------- #
	#                                 MAIN CLASSEs                                 #
	# ---------------------------------------------------------------------------- #

	def variable(self, children):
		identity = children[0]
		verse = children[1]
		if not verse:
			raise CordeliaTransformerError(f"statement '{identity}' has no items!")  
		return Variable(identity=identity, value=verse.items)

	def instrument(self, children):
		identity = children[0]
		rest = children[1:]

		modifiers = []
		verses = []

		for c in rest:
			if isinstance(c, Modifier):
				modifiers.append(c)
			elif isinstance(c, Verse):
				verses.append(c)
			else:
				raise CordeliaTransformerError(f"unexpected child in phrase '{identity.name}': {c!r}")
		if not verses:
			raise CordeliaTransformerError(f"phrase '{identity.name}' has no qualities!")

		return Instrument(
			identity=identity,
			modifiers=modifiers,
			verses=verses,
		)

_expander = MacroExpander()
_transformer = CordeliaTransformer()

def build(tree) -> Instrument | Variable:
	_expander.visit(tree)
	node = _transformer.transform(tree)
	node.validate()
	return node
