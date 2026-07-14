import pytest
from lark.exceptions import UnexpectedInput
from cordelia.pipeline.parser import parse
from cordelia.pipeline.transformer import transform
from cordelia.console import console
from cordelia.pipeline.transformer import *

# ---------------------------------------------------------------------------- #
#                              without transformer                             #
# ---------------------------------------------------------------------------- #

def test_simple():
	code = r"""
@tiny·talea {1 2 3} 16 in 8
"""
	poems = parse(code)
	for poem in poems:
		console.print(poem)
		poem = transform(poem)
		console.print(poem)
		assert isinstance(poem, Instrument)

def test_name_id():
	code = r"""
@tiny#2·talea {1 2 3} 16 in 8
"""
	poems = parse(code)
	for poem in poems:
		console.print(poem)
		poem = transform(poem)
		console.print(poem)
		assert isinstance(poem, Instrument)
		assert poem.cordelia_id == 2


def test_func_one_value():
	code = r"""
@tiny·talea {1 2 3} 16 in 8·osc{1}
"""
	poems = parse(code)
	for poem in poems:
		console.print(poem)
		poem = transform(poem)
		console.print(poem)
		assert isinstance(poem, Instrument)
		assert poem.qualities[1].args[0], Func
		assert poem.qualities[1].args[0].args[0] == '1'

def test_func_values():
	code = r"""
@tiny·talea {1 2 3} 16 in 8·osc{1 2}
"""
	poems = parse(code)
	for poem in poems:
		console.print(poem)
		poem = transform(poem)
		console.print(poem)
		assert isinstance(poem, Instrument)
		assert poem.qualities[1].args[0], Func
		assert poem.qualities[1].args[0].args[0] == '1'
		assert poem.qualities[1].args[0].args[1] == '2'


def test_var():
	code = r"""
@tiny·talea {1 2 3} 16 in 8·osc{1 2}

@var osc{tst}

"""
	poems = parse(code)
	
	transformed = []
	for poem in poems:
		console.print(poem)
		poem = transform(poem)
		console.print(poem)
		transformed.append(poem)

	assert isinstance(transformed[0], Instrument)

	assert isinstance(transformed[1], Variable)
	assert isinstance(transformed[1].args[0], Func)


def test_repeat_num():
	code = r"""
@tiny·talea {1 2 3} 16 in 8·osc{1 2^2}·alias 2? 1m
"""
	poems = parse(code)
	transformed = []
	for poem in poems:
		console.print(poem)
		poem = transform(poem)
		console.print(poem)
		transformed.append(poem)
	assert isinstance(transformed[0], Instrument)
	assert len(transformed[0].qualities[2].args) == 3

def test_repeat_str():
	code = r"""
@tiny·talea {1 2 3} 16 in 8·osc{1 cls^3 1 2^2}·alias 2? 1m
"""
	poems = parse(code)
	transformed = []
	for poem in poems:
		console.print(poem)
		poem = transform(poem)
		console.print(poem)
		transformed.append(poem)
	assert isinstance(transformed[0], Instrument)
	assert len(transformed[0].qualities[2].args) == 3