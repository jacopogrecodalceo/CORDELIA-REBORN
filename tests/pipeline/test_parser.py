import pytest
from pathlib import Path
from lark import Tree
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

   trees = parse(code)
   console.print(f"\nTREES: {len(trees)}")
   for t in trees:
      console.print(t)
   assert len(trees) == 1

def test_full_comment_remove():
   code = r"""
@cordelia·talea {1 2 3} 16 in 8
;@cordelia
talea {1 2 3} 16 in 8
@cordelia·talea {1 2 3} 16 in 8
"""
   trees = parse(code)
   console.print(f"\nTREES: {len(trees)}")
   for t in trees:
      console.print(t)
   assert len(trees) == 2


def test_complex():
   code = code_complex.read_text()
   trees = parse(code)
   console.print(f"\nTREES: {len(trees)}")
   for t in trees:
      console.print(t)
   assert len(trees) > 0

def test_ancient_cordelia():
   code = code_ancient_cordelia.read_text()
   trees = parse(code)
   console.print(f"\nTREES: {len(trees)}")
   for t in trees:
      console.print(t)
   assert len(trees) > 0

