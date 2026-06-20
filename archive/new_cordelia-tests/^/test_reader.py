from cordelia.reader import read

# --- single instrument ---

def test_single_instrument_with_score():
   code = """
@cordelia talea 3 1
   """
   expected = ["@cordelia talea 3 1"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

def test_single_instrument_no_score():
   code = """
@cordelia
   """
   expected = ["@cordelia"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

def test_instrument_score_on_next_line():
   code = """
@cordelia
talea 3 1
classic
   """
   expected = ["@cordelia talea 3 1 classic"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

def test_two_instruments_inline():
   code = """
@cordelia talea 3 1 @vermillon eu 3 10
   """
   expected = ["@cordelia talea 3 1", "@vermillon eu 3 10"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

def test_two_instruments_multiline():
   code = """
@cordelia
talea 3 1
@vermillon
eu 3 10
   """
   expected = ["@cordelia talea 3 1", "@vermillon eu 3 10"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

def test_instruments_joined_by_and():
   code = """
@cordelia and @vermillon talea 3 1
   """
   expected = ["@cordelia and @vermillon talea 3 1"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

def test_instruments_joined_by_comma():
   code = """
@cordelia, @vermillon talea 3 1
   """
   expected = ["@cordelia, @vermillon talea 3 1"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

def test_instruments_space_separated():
   code = """
@cordelia @vermillon talea 3 1
   """
   expected = ["@cordelia @vermillon talea 3 1"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

# --- single variable ---

def test_single_variable_no_value():
   """one variable with no value"""
   code = """
#p
   """
   expected = ["#p"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

def test_single_variable_with_value():
   code = """
#p 120
   """
   expected = ["#p 120"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

def test_two_variables_inline():
   code = """
#p 120 #bpm 60
   """
   expected = ["#p 120", "#bpm 60"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

# --- mixed ---

def test_instrument_and_variable_same_line():
   code = """
@cordelia talea 3 4 #variable 2
   """
   expected = ["@cordelia talea 3 4", "#variable 2"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

def test_instrument_parallel():
   code = """
@cordelia, @cordelia talea 3 4 #variable 2
   """
   expected = ["@cordelia, @cordelia talea 3 4", "#variable 2"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

def test_instrument_simultaneous():
   code = """
@cordelia @cordelia talea 3 4 #variable 2
@cordelia@cordelia talea 3 4 #variable 2
   """
   expected = ["@cordelia @cordelia talea 3 4", "#variable 2", "@cordelia@cordelia talea 3 4", "#variable 2"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

def test_instrument_sequence():
   code = """
@cordelia x2 and @cordelia talea 3 4 #variable 2
   """
   expected = ["@cordelia and @cordelia talea 3 4", "#variable 2"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

def test_variable_before_instrument():
   code = """
#p 120
@cordelia talea 3 1
   """
   expected = ["#p 120", "@cordelia talea 3 1"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

# --- sharp handling ---

def test_sharp_in_score_not_a_block():
   code = """
@cordelia talea 3, 4 d#4 1 3# 4 #variable 2
   """
   expected = ["@cordelia talea 3, 4 d#4 1 3# 4", "#variable 2"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

# --- whitespace handling ---

def test_blank_lines_between_blocks():
   code = """
@cordelia talea 3 1

@vermillon eu 3 10
   """
   expected = ["@cordelia talea 3 1", "@vermillon eu 3 10"]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected

def test_trailing_whitespace():
   """trailing whitespace is stripped"""
   code = """
#p 120
@cordelia, @cordelia talea 3 1
@cordelia talea 3 1
@cordelia talea 3, 4 d#4 1 3# 4
   """
   expected = [
      "#p 120",
      "@cordelia, @cordelia talea 3 1",
      "@cordelia talea 3 1",
      "@cordelia talea 3, 4 d#4 1 3# 4",
   ]
   result = read(code)
   print(f"\n  result:   {result}")
   assert result == expected