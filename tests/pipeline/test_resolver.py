import pytest
from lark.exceptions import UnexpectedInput
from cordelia.pipeline.parser import parse
from cordelia.pipeline.transformer import transform
from cordelia.pipeline.resolver import resolve
from cordelia.console import console
from cordelia.models.ast import *
from cordelia.runtime import queue, tracker
# ---------------------------------------------------------------------------- #
#                              without transformer                             #
# ---------------------------------------------------------------------------- #

def test_simple1():
   code = r"""
@aaron2·eu 3 8 in 8

@aaron·eu 5 8 in 8·hz 300 400
"""
   trees_parsed = parse(code)
   console.print(f"\nPARSED TREES: {len(trees_parsed)}")
   for t in trees_parsed:
      console.print(t)
      
   trees = transform(trees_parsed)
   console.print(f"\nTRANSFORMERs: {len(trees)}")
   for t in trees:
      resolve(t)
      console.print(t)
   console.print(queue)
   console.print(tracker)
         
   assert len(trees) == 2

def test_simple2():
   code = r"""
@aaron.am:radio{osc{1 1/8 lear}}·eu 5 8 in 8·hz 300 400

@aaron.am:radio{osc{1 1/8 lear}}·eu 5 8 in 8·hz 300 400
"""
   trees_parsed = parse(code)
   console.print(f"\nPARSED TREES: {len(trees_parsed)}")
   for t in trees_parsed:
      console.print(t)
      
   trees = transform(trees_parsed)
   console.print(f"\nTRANSFORMERs: {len(trees)}")
   for t in trees:
      resolve(t)
      console.print(t)
   console.print(queue)
   console.print(tracker)
   assert len(trees) == 2

def test_simple3():
   code = r"""
@aaron.am:radio{osc{1 1/8 lear}}·eu 5 8 in 8·eu 3 8 in 4·hz 300 400·dur*2·cls x2
"""
   trees_parsed = parse(code)
   console.print(f"\nPARSED TREES: {len(trees_parsed)}")
   for t in trees_parsed:
      console.print(t)
      
   trees = transform(trees_parsed)
   console.print(f"\nTRANSFORMERs: {len(trees)}")
   for t in trees:
      resolve(t)
      console.print(t)
   console.print(queue)
   console.print(tracker)
   assert len(trees) == 1

def test_process_score():
   code = r"""
@aaron.am:radio{osc{1 1/8 lear}}·eu 5 8 in 8·eu 3 8 in 4·hz 300 400·dur*2·cls x2
"""
   trees_parsed = parse(code)
   console.print(f"\nPARSED TREES: {len(trees_parsed)}")
   for t in trees_parsed:
      console.print(t)
      
   trees = transform(trees_parsed)
   console.print(f"\nTRANSFORMERs: {len(trees)}")
   for t in trees:
      resolve(t)
      t.score.process()
      console.print(t)

   assert len(trees) == 1
