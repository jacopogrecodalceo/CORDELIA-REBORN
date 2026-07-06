import pytest
from pathlib import Path
from lark import Tree
from lark.exceptions import UnexpectedInput
from cordelia.pipeline.parser import parse, parse_raw
from cordelia.console import console
from cordelia.pipeline.transformer import Instrument, Quality, Variable, Array, Func

def test_simple1():
	code = r"""
@aaron·talea 1 2x10 1
"""
	units = parse(code)
	console.print(units)
	assert len(units) == 1
	assert units[0].name == 'aaron'
	assert len(units[0].qualities[0].items) == 13

def test_simple2():
	code = r"""
@aaron2·talea {1 2x2 3 {4x4 2}} 16 in 8·dorian 1 2x3
@var 12x4
"""
	units = parse(code)
	console.print(units)
	assert len(units) == 2
	assert len(units[0].qualities[1].items) == 5


def test_simple3():
	code = r"""
@aaron2.fl{1x2 3 4}·talea {1 2x2 3 {4x4 2}} 16 in 8·dorian 1 2x3
@var 12x4
"""
	units = parse(code)
	console.print(units)
	assert len(units) == 2
	assert len(units[0].qualities[1].items) == 5

def test_simple4():
	code = r"""
@aaron2.fl{1x2 3 4}·talea {1 2x2 3 {4x4 2}} 16 in 8·dorian 1 2x3·cls x2 fin
@var 12x4
"""
	units = parse(code)
	console.print(units)
	assert len(units) == 2
	assert len(units[0].qualities[1].items) == 5

