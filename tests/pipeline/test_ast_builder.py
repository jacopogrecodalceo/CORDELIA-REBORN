import pytest
from lark.exceptions import UnexpectedInput
from cordelia.pipeline.frontend.lexer import lex
from cordelia.pipeline.frontend.parser import parse
from cordelia.pipeline.frontend.ast_builder import build, Func, Expr
from cordelia.console import console

from cordelia.models.nodes import Instrument, Variable
# ---------------------------------------------------------------------------- #
#                              without builder                             #
# ---------------------------------------------------------------------------- #

def test_instr():
	code = r"""
@tiny·talea {1 2 3^7} 16 in 8
"""
	chunks = lex(code)
	lines = parse(chunks)
	nodes = []
	for line in lines:
		console.print(line)
		node = build(line)
		console.print(node)
		nodes.append(node)
	assert isinstance(nodes[0], Instrument)

def test_instr_id():
	code = r"""
@tiny#2·talea {1 2 3^7} 16 in 8
"""
	chunks = lex(code)
	lines = parse(chunks)
	nodes = []
	for line in lines:
		console.print(line)
		node = build(line)
		console.print(node)
		nodes.append(node)
	assert isinstance(nodes[0], Instrument)

def test_repeat_in_mod():
	code = r"""
@tiny.def{2^2}·talea {1 2 3^7} 16 in 8
"""
	chunks = lex(code)
	lines = parse(chunks)
	nodes = []
	for line in lines:
		console.print(line)
		node = build(line)
		console.print(node)
		nodes.append(node)
	assert isinstance(nodes[0], Instrument)
