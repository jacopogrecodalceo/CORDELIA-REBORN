from cordelia.pipeline.parser import parse
from cordelia.pipeline.grouper import group, Group

def test_single_name_with_score():
   code = """
@cordelia talea 3 1 in 3
   """
   result = group(parse(code))
   print(f"\n  result: {result}")
   assert result == [Group(name="cordelia", score="talea 3 1 in 3")]

def test_single_name_no_score():
   code = """
@cordelia
   """
   result = group(parse(code))
   print(f"\n  result: {result}")
   assert result == [Group(name="cordelia", score=None)]

def test_two_staves_each_with_score():
   code = """
@cordelia talea 3 1 @vermillon eu 3 10
   """
   result = group(parse(code))
   print(f"\n  result: {result}")
   assert result == [
      Group(name="cordelia", score="talea 3 1"),
      Group(name="vermillon", score="eu 3 10"),
   ]

def test_two_staves_second_gets_score():
   code = """
@cordelia @vermillon talea 3 1
   """
   result = group(parse(code))
   print(f"\n  result: {result}")
   assert result == [
      Group(name="cordelia", score=None),
      Group(name="vermillon", score="talea 3 1"),
   ]

def test_two_staves_no_score():
   code = """
@cordelia @vermillon
   """
   result = group(parse(code))
   print(f"\n  result: {result}")
   assert result == [
      Group(name="cordelia", score=None),
      Group(name="vermillon", score=None),
   ]

def test_variable_name():
   code = """
@p 120
   """
   result = group(parse(code))
   print(f"\n  result: {result}")
   assert result == [Group(name="p", score="120")]

def test_mixed_staves_and_variables():
   code = """
@p 120 @cordelia talea 3 1
   """
   result = group(parse(code))
   print(f"\n  result: {result}")
   assert result == [
      Group(name="p", score="120"),
      Group(name="cordelia", score="talea 3 1"),
   ]

def test_multiline_score():
   code = """
@cordelia talea 3 1
eu 3 10
   """
   result = group(parse(code))
   print(f"\n  result: {result}")
   assert result == [Group(name="cordelia", score="talea 3 1\neu 3 10")]

def test_sharp_in_score():
   code = """
@cordelia talea 3, 4 d#4 1 3# 4
   """
   result = group(parse(code))
   print(f"\n  result: {result}")
   assert result == [Group(name="cordelia", score="talea 3, 4 d#4 1 3# 4")]

def test_mod():
   code = f"""
@cordelia.lpf()
:del()
:radio()
talea 3, 4 d#4 1 3# 4
   """
   result = group(parse(code))
   print(f"\n  result: {result}")
   assert result == [Group(name="cordelia", score=".lpf()\n:del()\n:radio()\ntalea 3, 4 d#4 1 3# 4")]