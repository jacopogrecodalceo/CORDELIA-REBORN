import pytest
from pathlib import Path
from lark import Tree
from lark.exceptions import UnexpectedInput
from cordelia.pipeline.parser import parse, parse_raw
from cordelia.pipeline.transformer import Instrument, Quality, Variable, Array, Func
from cordelia.console import console


code_complex = Path(__file__).parent / "code_complex.txt"
code_ancient_cordelia = Path(__file__).parent / "code_ancient_cordelia.txt"

def test_simple():
   code = r"""
@cordelia·talea {1 2 3}
"""
   trees = parse(code)
   console.print(f"\nTREES: {len(trees)}")
   for t in trees:
      console.print(t)

def test_more_difficult():
   code = r"""
@cordelia·talea {1 2 3}
@cordelia·eu 3 8
"""
   units = parse(code)
   console.print(f"\nTREES: {len(units)}")
   for u in units:
      console.print(u)
   assert isinstance(units[0], Instrument)
   assert isinstance(units[1], Instrument)

def test_v1():
   code = r"""
@cordelia·talea {1 2 3}
@cordelia·eu 3 8
@var osc{123 12}
@cordelia.lpf{1k}.radio·osc{123 12}·var 3 {1 23 3} 1 c..
@var osc{123 12}
"""
   units = parse(code)
   console.print(f"\nTREES: {len(units)}")
   for u in units:
      console.print(u)
   assert isinstance(units[0], Instrument)
   assert isinstance(units[1], Instrument)
   assert isinstance(units[2], Variable)
   assert isinstance(units[2].value[0], Func)
   assert isinstance(units[3], Instrument)
   assert units[3].name == 'cordelia'
   assert isinstance(units[3].score[0], Quality)
   trees = parse_raw(code)
   for t in trees:
      console.print(t)
