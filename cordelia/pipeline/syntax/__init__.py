from cordelia.pipeline.syntax.lexer import lex
from cordelia.pipeline.syntax.parser import parse
from cordelia.pipeline.syntax.ast_builder import build

def compile(code):
	lines = lex(code)

	# parsed tokens with grammar
	trees = parse(lines)

	# typed node (instrument | variable) & validation & macro expansion
	nodes = [build(tree) for tree in trees]

	return nodes
