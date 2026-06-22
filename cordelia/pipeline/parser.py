from lark import Lark
from loguru import logger
from cordelia.pipeline.lexer import lex
from cordelia.pipeline.transformer import CordeliaTransformer
import cordelia.path

GRAMMAR_PATH = cordelia.path.src / 'pipeline' / 'grammar.lark'
logger.debug(GRAMMAR_PATH)

_transformer = CordeliaTransformer()

def _build(transformer=None):
	grammar = GRAMMAR_PATH.read_text()
	return Lark(grammar, start="unit", parser="lalr", transformer=transformer)

def parse(source: str) -> list:
	p = _build(transformer=_transformer)
	return [p.parse(chunk) for chunk in lex(source)]

def parse_no_transformer(source: str) -> list:
	p = _build()
	return [p.parse(chunk) for chunk in lex(source)]