import pytest
from pathlib import Path
from lark import Tree
from lark.exceptions import UnexpectedInput
from cordelia.pipeline.parser import parse, parse_raw
from cordelia.console import console

from cordelia.pipeline.transformer import Instrument, Quality, Variable, Array, Func

code_complex = Path(__file__).parent / "code_complex.txt"
code_ancient_cordelia = Path(__file__).parent / "code_ancient_cordelia.txt"

# ---------------------------------------------------------------------------- #
#                              without transformer                             #
# ---------------------------------------------------------------------------- #

def test_simple_raw():
	code = r"""
@cordelia·talea {1 2 3} 16 in 8
"""
	trees = parse_raw(code)
	console.print(f"\nTREES: {len(trees)}")
	for t in trees:
		console.print(t)
	assert len(trees) == 1
	assert trees[0].data == 'phrase'

def test_simple():
	code = r"""
@cordelia·talea {1 2 3} 16 in 8
"""
	units = parse(code)
	console.print(f"\nUNITs: {len(units)}")
	for t in units:
		console.print(t)
	assert len(units) == 1
	assert isinstance(units[0], Instrument)
	instrument = units[0]

def test_check_quality():
	code = r"""
@cordelia·talea {1 2 3} 16 in 8
"""
	units = parse(code)
	console.print(f"\nUNITs: {len(units)}")
	for t in units:
		console.print(t)
	assert len(units) == 1
	assert isinstance(units[0], Instrument)
	instrument = units[0]
	assert isinstance(instrument.score[0], Quality)
	assert instrument.score[0].items[0] == 'talea'

def test_check_repeat1():
	code = r"""
@cordelia·talea {1 2*2 3} 16 in 8
"""
	units = parse(code)
	console.print(f"\nUNITs: {len(units)}")
	for t in units:
		console.print(t)
	assert len(units) == 1
	assert isinstance(units[0], Instrument)
	instrument = units[0]
	assert isinstance(instrument.score[0], Quality)
	assert instrument.score[0].items[0] == 'talea'

def test_check_repeat2():
	code = r"""
@cordelia·talea {1 2*3 3} 16 in 8·dorian f*2
"""
	units = parse(code)
	console.print(f"\nUNITs: {len(units)}")
	for t in units:
		console.print(t)
	assert len(units) == 1
	assert isinstance(units[0], Instrument)
	instrument = units[0]
	assert isinstance(instrument.score[0], Quality)
	assert instrument.score[0].items[0] == 'talea'

def test_various_space():
	code = r"""
	@cordelia ·talea  {1  2x3 3 } 16  in 8· dorian fx2 
"""
	units = parse(code)
	console.print(f"\nUNITs: {len(units)}")
	for t in units:
		console.print(t)
	assert len(units) == 1
	assert isinstance(units[0], Instrument)
	instrument = units[0]
	assert isinstance(instrument.score[0], Quality)
	assert instrument.score[0].items[0] == 'talea'

def test_multiline():
	code = r"""
	@cordelia ·talea  {1  2x3 3 } 16  in 8· dorian fx2 
	
		@pulse 100+jit{20 1/8}
"""
	units = parse(code)
	console.print(f"\nUNITs: {len(units)}")
	for t in units:
		console.print(t)
	assert len(units) == 2
	assert isinstance(units[0], Instrument)
	instrument = units[0]
	assert isinstance(instrument.score[0], Quality)
	assert instrument.score[0].items[0] == 'talea'

def test_func():
	code = r"""
	@cordelia ·talea  {1  2x3 3 osc{1 2}} 16  in 8· dorian fx2 
	
		@pulse 100+jit{20 1/8}
"""
	units = parse(code)
	console.print(f"\nUNITs: {len(units)}")
	for t in units:
		console.print(t)
	assert len(units) == 2
	assert isinstance(units[0], Instrument)
	instrument = units[0]
	assert isinstance(instrument.score[0], Quality)
	assert instrument.score[0].items[0] == 'talea'
	assert isinstance(instrument.score[0].items[1], Array)
	array = instrument.score[0].items[1]
	console.print('='*128)
	console.print(array)
	assert array.items[5].name == 'osc'

def test_ancient_cordelia1():
	"""

gktuning = scala.edolin12

eu: 4, 16, 8
	@careless@synthi.flanij(oscili:k(1/6, 1/32, lear), lfh(16));.shij(qn)
	wn*4
	p
	hader.a(5)
	step(c3, locrian, random:k(0, 9))
	"""
	
	code = r"""
		@pulse 40+jit{20 1/8}+alea{-30 10 1/16}

@scala {edolin12 edo31 pto_diat} in 8
  
@careless.fl{osc{1/6 1/32 lear} lf{16}} ·eu  4 16 in 8· locrian c 9?·hader.a5d35s5r·p·wn*4 
	
"""
	units = parse(code)
	console.print(f"\nUNITs: {len(units)}")
	for t in units:
		console.print(t)
	assert len(units) == 3
	assert isinstance(units[0], Variable)
	assert isinstance(units[2], Instrument)
	instrument = units[2]
	assert isinstance(instrument.score[0], Quality)
	assert instrument.score[0].items[0] == 'eu'
