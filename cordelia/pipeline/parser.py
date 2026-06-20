from pathlib import Path
from lark import Lark
from loguru import logger

CORDELIA_SRC_DIR = Path(__file__).parent.parent
GRAMMAR_PATH = CORDELIA_SRC_DIR / "grammar" / "tokens.lark"
logger.debug(GRAMMAR_PATH)
def build_parser():
	grammar = GRAMMAR_PATH.read_text()
	return Lark(grammar, start="code", parser="lalr")

def parse(source: str):
	parser = build_parser()
	return parser.parse(source)