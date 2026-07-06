import pytest
from pathlib import Path
from lark import Tree
from lark.exceptions import UnexpectedInput
from cordelia.pipeline.parser import parse, parse_raw
from cordelia.pipeline.transformer import Instrument, Variable
from cordelia.console import console

# ---------------------------------------------------------------------------- #
#                              without transformer                             #
# ---------------------------------------------------------------------------- #

def test_specific1():
   code = r"""
@cordelia.lpf:del{qn}:radio{}·talea {3 1 0x6} in 8·dorian d 1 7 3·dorian {1 3 9} func{1 2 3}
"""

   trees = parse_raw(code)
   console.print(f"\nTREES: {len(trees)}")
   for t in trees:
      console.print(t)
   result = parse_raw(code)
   assert len(result) == 1 #one phrase
   
   print("-"*128)
   unit = trees[0]
   assert unit.data == 'phrase'
   phrase = unit
   assert phrase.children[0].data == 'header'
   assert phrase.children[1].data == 'modifier'
   assert phrase.children[4].data == 'score'
   print("-"*128)

def test_specific2():
   code = r"""
@cordelia.lpf:del{qn}:radio{}
talea {3 1 0x6} in 8·dorian d 1 7 3
dorian {1 3 9}
@cordelia.lpf
:del{qn}
:radio{}
talea {3 1 0x6} in 8
dorian d 1 7 3
dorian {1 3 9}
"""

   trees = parse_raw(code)
   console.print(f"\nTREES: {len(trees)}")
   for t in trees:
      console.print(t)
   result = parse_raw(code)
   assert len(result) == 2 #one phrase
   
   print("-"*128)
   unit = trees[0]
   assert unit.data == 'phrase'
   phrase = unit
   assert phrase.children[0].data == 'header'
   assert phrase.children[1].data == 'modifier'
   assert phrase.children[4].data == 'score'
   print("-"*128)

def test_specific3():
   code = r"""
@cordelia.lpf:del{qn}:radio·talea {3 1 0x6} in 8·dorian d 1 7 3x2
"""

   trees = parse_raw(code)
   console.print(f"\nTREES: {len(trees)}")
   for t in trees:
      console.print(t)
   result = parse_raw(code)
   assert len(result) == 1 #one phrase
   
   print("-"*128)
   unit = trees[0]
   assert unit.data == 'phrase'
   phrase = unit
   assert phrase.children[0].data == 'header'
   assert phrase.children[1].data == 'modifier'
   assert phrase.children[4].data == 'score'
   print("-"*128)

"""
now make the same test but with NEWLINE separator, please
"""