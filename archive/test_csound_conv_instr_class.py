import pytest
from pathlib import Path
from lark import Tree
from lark.exceptions import UnexpectedInput
from cordelia.pipeline.parser import parse, parse_raw
from cordelia.console import console
from archive.processor.run import process
import archive.post_processor
import cordelia.csound_conversion.instrument_class
from cordelia.pipeline.transformer import Instrument, Quality, Variable, Array, Func
import cordelia.session.instrument_tracker as instrument_tracker

def test_simple1():
	code = r"""
@aaron·eu 3 8·dur={1 2 3}
"""
	units = parse(code)
	assert len(units) == 1
	for unit in units:
		process(unit)
		archive.post_processor.run(unit)
		cordelia.csound_conversion.instrument_class.convert(unit)
	for unit in units:
		process(unit)
		archive.post_processor.run(unit)
		cordelia.csound_conversion.instrument_class.convert(unit)
	console.print(units)
	instrument_tracker.clear()

