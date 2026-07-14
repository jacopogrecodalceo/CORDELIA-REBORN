from lark import Transformer
from dataclasses import dataclass, field
from typing import Any

from cordelia.models.instrument import Instrument, Modifier
from cordelia.models.variable import Variable

from cordelia.console import console
from cordelia.registry import data
from cordelia.errors import *

# ---------------------------------------------------------------------------- #
#                                    MODELs                                    #
# ---------------------------------------------------------------------------- #
@dataclass
class QualityRaw:
	items: list[Any] = field(default_factory=list)

@dataclass
class Func:
	name: str
	items: list[Any] = field(default_factory=list)

@dataclass
class Expr:
	items: list

class Repeat(list):
	def __init__(self, value, times):
		super().__init__([value] * times)

# ---------------------------------------------------------------------------- #
#                                    HELPERs                                   #
# ---------------------------------------------------------------------------- #

def _resolve_repeat(items: list):
	resolved = []
	for x in items:
		if isinstance(x, Repeat):
			resolved.extend(x)
		else:
			resolved.append(x)
	return resolved

def _validate(what: str, name: str):
	if not data[what].get(name):
		raise CordeliaValidationError(f'cannot find {name} in {what} json · probably a typing error?')

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

	def INVOCATION_KIND(self, token):
		# children[0] is a Token holding the literal "." or ":"
		symbol = str(token)
		return "serial" if symbol == "." else "parallel"

	# ---------------------------------------------------------------------------- #
	#                                     RULEs                                    #
	#   contract: only rules that ASSEMBLE a fresh list from raw children call     #
	#   expand(). every other rule trusts its children unchanged. expr never       #
	#   returns a bare list -- single term passes through, multi-term becomes an   #
	#   Expr node, so expand() can never mistake an infix chain for an array.      #
	# ---------------------------------------------------------------------------- #
	def func(self, children):
		name = str(children[0])
		items = children[1]
		return Func(name=name, items=items)

	def array(self, children):
		items = list(children)
		return items

	def foot(self, children):
		items = list(children)
		if len(items) == 1:
			return items[0]
		return Expr(items=items)
		#return list(items)

	def repeat(self, children):
		value = children[0]
		times = int(children[1][1:])
		return Repeat(value, times)

	# ---------------------------------------------------------------------------- #
	#                                   QUALITIEs                                  #
	# ---------------------------------------------------------------------------- #

	def verse(self, children):
		items = list(children)
		return QualityRaw(items=items)

	# ---------------------------------------------------------------------------- #
	#                                   EPIGRAPH                                   #
	# ---------------------------------------------------------------------------- #

	def cordelia_id(self, children):
		return int(children[0])

	def epigraph(self, children):
		return str(children[0])

	# ---------------------------------------------------------------------------- #
	#                                   MODIFIERs                                  #
	# ---------------------------------------------------------------------------- #

	def invocation(self, children):
		kind = children[0]
		name = str(children[1])
		_validate('modifier', name)  
		array = children[2] if len(children) > 2 else None
		return Modifier(kind=kind, name=name, items=array)

	# ---------------------------------------------------------------------------- #
	#                                 MAIN CLASSEs                                 #
	# ---------------------------------------------------------------------------- #

	def statement(self, children):
		name = children[0]
		quality = children[1]
		if not quality:
			raise CordeliaTransformerError(f"statement '{name}' has no items!")  
		return Variable(name=name, items=quality.items)

	def phrase(self, children):
		name = children[0]
		_validate('instrument', name)
		rest = children[1:]

		modifiers = []
		qualities_raw = []
		cordelia_id=1
		for c in rest:
			if isinstance(c, int):
				cordelia_id=c
			elif isinstance(c, Modifier):
				modifiers.append(c)
			elif isinstance(c, QualityRaw):
				qualities_raw.append(c)
			else:
				raise CordeliaTransformerError(f"unexpected child in phrase '{name}': {c!r}")
		if not qualities_raw:
			raise CordeliaTransformerError(f"phrase '{name}' has no qualities!")

		return Instrument(name=name, cordelia_id=cordelia_id, modifiers=modifiers, qualities_raw=qualities_raw)

_transformer = CordeliaTransformer()
def transform(poem: str) -> Instrument | Variable:
	try:
		return _transformer.transform(poem)
	except Exception as e:
		console.print(f"[error]{e}[/error]")
		import traceback
		console.print(traceback.format_exc())
