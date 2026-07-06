import pytest
from pathlib import Path
from lark import Tree
from lark.exceptions import UnexpectedInput
from cordelia.pipeline.parser import parse, parse_raw
from cordelia.console import console
from archive.processor.run import process
import archive.post_processor
from cordelia.pipeline.transformer import Instrument, Quality, Variable, Array, Func
import cordelia.session.instrument_tracker as instrument_tracker

def test_simple():
	code = r"""
@aaron·eu 3 8·dur={1 2 3}
"""
	units = parse(code)

	assert len(units) == 1
	assert units[0].name == 'aaron'
	for unit in units:
		process(unit)
		archive.post_processor.run(unit)
		console.print(unit)
	assert units[0].score['dur'] == ['1', '2', '3']
	instrument_tracker.clear()

def test_eu1():
	code = r"""
@aaron·eu 3 8 in 8·dur*2
"""
	units = parse(code)

	assert len(units) == 1
	assert units[0].name == 'aaron'
	for unit in units:
		process(unit)
		archive.post_processor.run(unit)
		console.print(unit)
	instrument_tracker.clear()

def test_eu2():
	code = r"""
@aaron·eu 5 16 1 in 8·dur*2
"""
	units = parse(code)

	assert len(units) == 1
	assert units[0].name == 'aaron'
	for unit in units:
		process(unit)
		archive.post_processor.run(unit)
		console.print(unit)
	assert units[0].score['dur'] == [8, 6, 6, 6, 6]
	instrument_tracker.clear()

def test_eu3():
	code = r"""
@aaron·eu 3 8 in 8·dur*{4 1}·dorian d' 1 4·cls x2 
"""
	units = parse(code)

	assert len(units) == 1
	assert units[0].name == 'aaron'
	for unit in units:
		process(unit)
		archive.post_processor.run(unit)
		console.print(unit)
	assert units[0].score['dur'] == [12, 3, 8]
	instrument_tracker.clear()
