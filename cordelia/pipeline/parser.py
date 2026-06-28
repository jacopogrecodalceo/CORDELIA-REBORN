from lark import Lark, lexer
from loguru import logger
from cordelia.pipeline.lexer import lex
from cordelia.pipeline.transformer import CordeliaTransformer
import cordelia.path

GRAMMAR_PATH = cordelia.path.core / 'grammar.lark'
logger.debug(GRAMMAR_PATH)

_transformer = CordeliaTransformer()

grammar = GRAMMAR_PATH.read_text()
p = Lark(grammar, start="unit", parser="earley", lexer="dynamic", ambiguity="resolve")

def parse(source: str) -> list:
   return [_transformer.transform(p.parse(chunk)) for chunk in lex(source)]

def parse_raw(source: str) -> list:
   return [p.parse(chunk) for chunk in lex(source)]