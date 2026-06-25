from abjad import Instrument
import pytest
from cordelia.pipeline.parser import parse
from cordelia.pipeline.quality_models import *
from cordelia.console import console

def test_mode1():
   code = r"""
@cordelia·dorian d.. 1 2 3·talea {3 1} 8 in 8
"""
   units = parse(code)
   for u in units:
      console.print(u)
   assert isinstance(units[0].score[0], Colores)
   assert isinstance(units[0].score[1], Talea)

def test_mode2():
   code = r"""
@friren.fl{3 osc{2 3}}·locrian d.. 1 2 3 4 3 2 1·talea {3 1} 8 in 8
"""
   units = parse(code)
   for u in units:
      console.print(u)
   assert isinstance(units[0].score[0], Colores)
   assert isinstance(units[0].score[1], Talea)

def test_dur1():
   code = r"""
@double.fl{3 osc{2 3}}·locrian d.. 1 2x3 3 4 3 2 1·talea {3 1} 8 in 8·dur*2
"""
   units = parse(code)
   for u in units:
      console.print(u)
   assert isinstance(units[0].score[0], Colores)
   assert isinstance(units[0].score[1], Talea)

def test_dur1():
   code = r"""
@double.fl{3 osc{2 3}}:del{1}·locrian d.. 1 2x3 3 4 3 2 1·talea {3x2 1} 8 in 8·dur*2
"""
   units = parse(code)
   for u in units:
      console.print(u)
   assert isinstance(units[0].score[0], Colores)
   assert isinstance(units[0].score[1], Talea)

def test_env1():
   code = r"""
@double.fl{3 osc{2 3}}:del{1}·locrian d.. 1 2x3 3 4 3 2 1·talea {3x2 1} 8 in 8·dur*2·maigretx2
"""
   units = parse(code)
   for u in units:
      console.print(u)
   assert isinstance(units[0].score[0], Colores)
   assert isinstance(units[0].score[1], Talea)
   assert isinstance(units[0].score[3], Env)

def test_env2():
   code = r"""
@double.fl{3 osc{2 3}}:del{1}·locrian d.. 1 2x3 3 4 3 2 1·talea {3x2 1} 8 in 8·dur*2·maigretx2 classic likearev
"""
   units = parse(code)
   for u in units:
      console.print(u)
   assert isinstance(units[0].score[0], Colores)
   assert isinstance(units[0].score[1], Talea)
   assert isinstance(units[0].score[3], Env)

def test_dyn1():
   code = r"""
@double.fl{3 osc{2 3}}:del{1}·locrian d'' 1 2x3 3 4 3 2 1·talea {3x2 1} 8 in 8·dur*2·maigretx2 classic likearev·mf
"""
   units = parse(code)
   for u in units:
      console.print(u)
   assert isinstance(units[0].score[0], Colores)
   assert isinstance(units[0].score[1], Talea)
   assert isinstance(units[0].score[3], Env)
   assert isinstance(units[0].score[4], Dyn)

def test_dyn2():
   code = r"""
@double.fl{3 osc{2 3}}:del{1}·locrian d.. 1 2x3 3 4 3 2 1·talea {3x2 1} 8 in 12·dur*2·maigretx2 classic likearev·mf f pp fx3
"""
   units = parse(code)
   for u in units:
      console.print(u)
   assert isinstance(units[0].score[0], Colores)
   assert isinstance(units[0].score[1], Talea)
   assert isinstance(units[0].score[3], Env)
   assert isinstance(units[0].score[4], Dyn)


