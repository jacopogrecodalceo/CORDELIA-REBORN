import pytest
from lark.exceptions import UnexpectedInput

import cordelia.pipeline.syntax as syntax
import cordelia.pipeline.analysis as analysis

from cordelia.models.types import *
from cordelia.console import console

from cordelia.models.nodes import Instrument, Variable
# ---------------------------------------------------------------------------- #
#                              without transformer                             #
# ---------------------------------------------------------------------------- #

def test_instr():
   code = r"""
@tiny·eu 3 8 in 8·hz 300·eu 3 4 in 3·eu 5 8 in 9·freq*2
"""
   nodes = syntax.compile(code)
   nodes = analysis.compile(nodes)
   console.print(nodes)
      
   assert isinstance(nodes[0], Instrument)

def test_grov():
   code = r"""
@tiny·eu 3 8 in 8
"""
   nodes = syntax.compile(code)
   nodes = analysis.compile(nodes)
   
   no_grov = [i for i, v in enumerate(nodes[0].talea.occurrencies[0].processed) if v]

   code = r"""
@tiny·eu 3 8 in 8·grov .25
"""
   nodes = syntax.compile(code)
   nodes = analysis.compile(nodes)
   grov = [i for i, v in enumerate(nodes[0].talea.occurrencies[0].processed) if v]
   console.print(grov, no_grov)
   assert grov != no_grov

def test_instr2():
   code = r"""
@tiny#2.del{8}·eu 3 8 in 8

"""
   nodes = syntax.compile(code)
   nodes = analysis.compile(nodes)

   for n in nodes:
      print(n.identity.uid, n.cycle.ftgen_format(n))      
   assert isinstance(nodes[0], Instrument)