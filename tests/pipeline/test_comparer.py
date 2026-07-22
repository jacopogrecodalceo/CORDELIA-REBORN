import pytest
from lark.exceptions import UnexpectedInput
from cordelia.pipeline.syntax import compile
from cordelia.console import console

from cordelia.models.nodes import Instrument, Variable
# ---------------------------------------------------------------------------- #
#                              without transformer                             #
# ---------------------------------------------------------------------------- #

def test_instr():
   code = r"""
@tiny·talea {1 2 3^7} 16 in 8
"""
   
   nodes = compile(code)
   print(nodes)
   console.print(nodes)
   
   assert isinstance(nodes[0], Instrument)
