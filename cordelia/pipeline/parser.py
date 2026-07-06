from lark import Lark
from cordelia.pipeline.lexer import lex
import cordelia.path

GRAMMAR_PATH = cordelia.path.core / 'grammar.lark'
grammar = GRAMMAR_PATH.read_text()
p = Lark(grammar, start="unit", parser="earley", lexer="dynamic", ambiguity="resolve")

def parse(source: str) -> list:
   return [p.parse(chunk) for chunk in lex(source)]

