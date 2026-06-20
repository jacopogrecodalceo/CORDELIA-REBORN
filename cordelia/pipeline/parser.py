from pathlib import Path
from lark import Lark
from loguru import logger

CORDELIA_SRC_DIR = Path(__file__).parent
GRAMMAR_PATH = CORDELIA_SRC_DIR / "grammar.lark"
logger.debug(GRAMMAR_PATH)
def build_parser():
	grammar = GRAMMAR_PATH.read_text()
	return Lark(grammar, start="program", parser="earley")

def parse(source: str):
	parser = build_parser()
	return parser.parse(source)