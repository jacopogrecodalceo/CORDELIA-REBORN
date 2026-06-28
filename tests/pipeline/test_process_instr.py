import pytest
from pathlib import Path
from lark import Tree
from lark.exceptions import UnexpectedInput
from cordelia.pipeline.parser import parse, parse_raw
from cordelia.console import console
from cordelia.pipeline.processor.run import process
from cordelia.pipeline.transformer import Instrument, Quality, Variable, Array, Func
import cordelia.session.instrument_tracker as instrument_tracker

def test_name():
	code = r"""
@aaron·talea {1 2 3} in 8
"""
	units = parse(code)
	trees = parse_raw(code)
	for t in trees:
		console.print(t)

	assert len(units) == 1
	assert units[0].name == 'aaron'
	for unit in units:
		process(unit)
	instrument_tracker.clear()

def test_validation_mod():
	code = r"""
@aaron.radio·talea {1 2 3} in 8
"""
	units = parse(code)
	trees = parse_raw(code)
	for t in trees:
		console.print(t)

	assert len(units) == 1
	assert units[0].name == 'aaron'
	for unit in units:
		process(unit)
	instrument_tracker.clear()

def test_validation_talea_and_eu():
	code = r"""
@aaron.radio·talea {1 2 3} in 8·eu 2 8 in 18
"""
	units = parse(code)

	assert len(units) == 1
	assert units[0].name == 'aaron'
	for unit in units:
		process(unit)
	instrument_tracker.clear()

def test_dyn():
	code = r"""
@aaron.radio·talea {1 2 3} in 8·eu 2 8 in 18·mf
"""
	units = parse(code)

	assert len(units) == 1
	assert units[0].name == 'aaron'
	for unit in units:
		process(unit)
	instrument_tracker.clear()

def test_dur_mul():
	code = r"""
@aaron.radio·talea {10x2 2 3} in 8·eu 2 8 in 18·mf·dur*3
"""
	units = parse(code)
	assert len(units) == 1
	assert units[0].name == 'aaron'
	for unit in units:
		process(unit)
	instrument_tracker.clear()


def test_dur_equal():
	code = r"""
@aaron.radio·talea {10x2 2 3} in 8 ·eu 2 8 in 18·mf·dur=3

@aaron#2.radio·talea {10x2 2 3} in 8·eu 2 8 in 18·mf·dur={1 2}

@aaron#3.radio·talea {10x2 2 3} in 8·eu 2 8 in 18·mf·dur*{1 2}

@aaron#4.radio·talea {10x2 2 3} in 8·eu 2 8 in 18·mf·dur/{1 2}
"""
	units = parse(code)

	assert len(units) == 4
	assert units[0].name == 'aaron'
	for unit in units:
		process(unit)
	instrument_tracker.clear()

def test_dur_keyword():
	code = r"""
@aaron.radio·talea {10x2 2 3} in 8·mf· wn qn

"""
	units = parse(code)

	assert len(units) == 1
	assert units[0].name == 'aaron'
	for unit in units:
		process(unit)
		console.print(unit)
		console.print(unit.score['dyn'])
		console.print(unit.score['dur'])
	instrument_tracker.clear()

def test_colores():
	code = r"""
@aaron.radio·talea {10x2 2 3} in 8·dorian c.. 1 3

"""
	units = parse(code)

	assert len(units) == 1
	assert units[0].name == 'aaron'
	for unit in units:
		process(unit)
		console.print(unit)
	instrument_tracker.clear()
