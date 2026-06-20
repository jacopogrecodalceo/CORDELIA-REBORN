import pytest
from cordelia.pipeline.parser import parse
from lark.exceptions import UnexpectedInput

def test_single_instrument():
   code = """
@cordelia talea 3 1 in 3
   """
   tree = parse(code)
   print(f"\n  tree:\n{tree.pretty()}")
   tokens = tree.children
   assert len(tokens) == 2
   assert tokens[0].children[0].data == "staff"
   assert tokens[1].children[0].data == "score"

def test_multiple_instruments():
   code = """
@cordelia talea 3 1 in 3

@cordelia talea 3 1 in 3
   """
   tree = parse(code)
   print(f"\n  tree:\n{tree.pretty()}")
   tokens = tree.children
   assert len(tokens) == 4
   assert tokens[0].children[0].data == "staff"
   assert tokens[1].children[0].data == "score"
   assert tokens[2].children[0].data == "staff"
   assert tokens[3].children[0].data == "score"

def test_various1():
   code = """
   @variable 2
   
@cordelia talea 3 1 in 3

@cordelia talea 3 1 in 3


@delay qn *2 in cordelia
   """
   tree = parse(code)
   print(f"\n  tree:\n{tree.pretty()}")
   tokens = tree.children
   assert len(tokens) == 8
