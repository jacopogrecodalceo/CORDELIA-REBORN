import pytest
from pathlib import Path
from lark import Tree
from lark.exceptions import UnexpectedInput
from cordelia.pipeline.parser import parse, parse_raw
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

   trees = parse_raw(code)
   console.print(f"\nTREES: {len(trees)}")
   for t in trees:
      console.print(t)
   result = parse_raw(code)
   assert len(result) > 0

def test_full_comment_remove():
   code = r"""
@cordelia·talea {1 2 3} 16 in 8
;@cordelia
talea {1 2 3} 16 in 8
@cordelia·talea {1 2 3} 16 in 8
"""

   trees = parse_raw(code)
   console.print(f"\nTREES: {len(trees)}")
   for t in trees:
      console.print(t)
   result = parse_raw(code)
   assert len(result) == 3


def test_complex():
   code = code_complex.read_text()

   trees = parse_raw(code)
   console.print(f"\nTREES: {len(trees)}")
   for t in trees:
      console.print(t)
   result = parse_raw(code)
   assert len(result) > 0

def test_old_cordelia():
   
   """
   eu: 4, 16, 8
   @careless@synthi.flanij(oscili:k(1/6, 1/32, lear), lfh(16));.shij(qn)
   wn*4
   p
   hader.a(5)
   step(c3, locrian, random:k(0, 9))
   """   

   code = code_ancient_cordelia.read_text()
   trees = parse_raw(code)
   console.print(f"\nTREES: {len(trees)}")
   for t in trees:
      console.print(t)
   result = parse_raw(code)
   assert len(result) > 0
