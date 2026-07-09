import pytest
from lark.exceptions import UnexpectedInput
from cordelia.pipeline.parser import parse
from cordelia.pipeline.transformer import transform
from cordelia.console import console
from cordelia.models.ast import *

# ---------------------------------------------------------------------------- #
#                              without transformer                             #
# ---------------------------------------------------------------------------- #

def test_simple():
   code = r"""
@cordelia·talea {1 2 3} 16 in 8
"""
   trees_parsed = parse(code)
   console.print(f"\nPARSED TREES: {len(trees_parsed)}")
   for t in trees_parsed:
      console.print(t)
      
   trees = transform(trees_parsed)
   console.print(f"\nTRANSFORMERs: {len(trees)}")
   for t in trees:
      console.print(t)
   assert len(trees) == 1

def test_name_id():
   code = r"""
@cordelia#2·talea {1 2 3} 16 in 8
"""
   trees_parsed = parse(code)
   console.print(f"\nPARSED TREES: {len(trees_parsed)}")
   for t in trees_parsed:
      console.print(t)
      
   trees = transform(trees_parsed)
   console.print(f"\nTRANSFORMERs: {len(trees)}")
   for t in trees:
      console.print(t)
   assert len(trees) == 1
   assert trees[0].name_id == 2

def test_func_one_value():
   code = r"""
@cordelia·talea {1 2 3} 16 in 8·osc{1}
"""
   trees_parsed = parse(code)
   console.print(f"\nPARSED TREES: {len(trees_parsed)}")
   for t in trees_parsed:
      console.print(t)
      
   trees = transform(trees_parsed)
   console.print(f"\nTRANSFORMERs: {len(trees)}")
   for t in trees:
      console.print(t)
   assert len(trees) == 1
   assert isinstance(trees[0].qualities[1].items[0], Func)
   assert trees[0].qualities[1].items[0].args[0] == '1'

def test_func_values():
   code = r"""
@cordelia·talea {1 2 3} 16 in 8·osc{1 2}
"""
   trees_parsed = parse(code)
   console.print(f"\nPARSED TREES: {len(trees_parsed)}")
   for t in trees_parsed:
      console.print(t)
      
   trees = transform(trees_parsed)
   console.print(f"\nTRANSFORMERs: {len(trees)}")
   for t in trees:
      console.print(t)
   assert len(trees) == 1
   assert isinstance(trees[0].qualities[1].items[0], Func)
   assert trees[0].qualities[1].items[0].args[0] == '1'
   assert trees[0].qualities[1].items[0].args[1] == '2'

def test_var():
   code = r"""
@cordelia·talea {1 2 3} 16 in 8·osc{1 2}
@var osc{tst}

"""
   trees_parsed = parse(code)
   console.print(f"\nPARSED TREES: {len(trees_parsed)}")
   for t in trees_parsed:
      console.print(t)
      
   trees = transform(trees_parsed)
   console.print(f"\nTRANSFORMERs: {len(trees)}")
   for t in trees:
      console.print(t)
   assert len(trees) == 2
   assert isinstance(trees[1].value[0], Func)
   assert trees[1].value[0].args[0] == 'tst'

def test_repeat_num():
   code = r"""
@cordelia·talea {1 2 3} 16 in 8·osc{1 2x2}·alias 2? 1m
"""
   trees_parsed = parse(code)
   console.print(f"\nPARSED TREES: {len(trees_parsed)}")
   for t in trees_parsed:
      console.print(t)
      
   trees = transform(trees_parsed)
   console.print(f"\nTRANSFORMERs: {len(trees)}")
   for t in trees:
      console.print(t)
   assert len(trees) == 1
   assert isinstance(trees[0].qualities[1].items[0], Func)
   assert len(trees[0].qualities[1].items[0].args) == 3

def test_repeat_str():
   code = r"""
@cordelia·talea {1 2 3} 16 in 8·osc{1 cls x3 1 2x2}·alias 2? 1m
"""
   trees_parsed = parse(code)
   console.print(f"\nPARSED TREES: {len(trees_parsed)}")
   for t in trees_parsed:
      console.print(t)
      
   trees = transform(trees_parsed)
   console.print(f"\nTRANSFORMERs: {len(trees)}")
   for t in trees:
      console.print(t)
   assert len(trees) == 1
   assert isinstance(trees[0].qualities[1].items[0], Func)
   assert trees[0].qualities[1].items[0].args[1] == 'cls'
   assert trees[0].qualities[1].items[0].args[2] == 'cls'
   assert trees[0].qualities[1].items[0].args[3] == 'cls'
   assert trees[0].qualities[1].items[0].args[4] == '1'
   assert trees[0].qualities[1].items[0].args[6] == '2'