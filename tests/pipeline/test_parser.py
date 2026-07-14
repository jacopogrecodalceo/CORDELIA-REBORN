import pytest
from lark import Tree
from pathlib import Path
from lark.exceptions import UnexpectedInput
from cordelia.pipeline.parser import parse
from cordelia.console import console

code_complex = Path(__file__).parent / "code_complex.txt"
code_ancient_cordelia = Path(__file__).parent / "code_ancient_cordelia.txt"

# ---------------------------------------------------------------------------- #
#                              without transformer                             #
# ---------------------------------------------------------------------------- #

def test_func_inside_qualities():
   code = r"""
@cordelia·talea {1 2 3} 16 in 8
"""
   poems = parse(code)
   console.print(f"\nPOEMs: {len(poems)}")
   for poem in poems:
      console.print(poem)
   assert len(poems) == 1

def test_complex():
   code = code_complex.read_text()
   poems = parse(code)
   console.print(f"\nPOEMs: {len(poems)}")
   for poem in poems:
      console.print(poem)
   assert len(poems) > 1

def test_ancient_cordelia():
   code = code_ancient_cordelia.read_text()
   poems = parse(code)
   console.print(f"\nPOEMs: {len(poems)}")
   for poem in poems:
      console.print(poem)
   assert len(poems) > 1

