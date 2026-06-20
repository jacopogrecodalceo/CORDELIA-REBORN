import pytest
from lark import Tree, Token
from lark.exceptions import UnexpectedInput
from cordelia.pipeline.parser import parse
from cordelia.console import console


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def get_units(tree):
   return [u.children[0] for u in tree.children]

def get_score_atoms(score):
   return [str(a.children[0]) for a in score.children]

def get_modifiers(phrase):
   return [c for c in phrase.children if isinstance(c, Tree) and c.data == "modifier"]

def get_scores(phrase):
   return [c for c in phrase.children if isinstance(c, Tree) and c.data == "score"]


# ─── SINGLE UNIT ─────────────────────────────────────────────────────────────

def test_single_instrument():
   code = "@cordelia·talea 3 1 in 3"
   tree = parse(code)
   units = get_units(tree)
   assert len(units) == 1
   assert units[0].data == "phrase"

def test_single_unit_header():
   code = "@cordelia·talea 3 1 in 3"
   tree = parse(code)
   phrase = get_units(tree)[0]
   assert phrase.children[0].data == "header"
   assert str(phrase.children[0].children[0]) == "cordelia"

def test_single_unit_score():
   code = "@cordelia·talea 3 1 in 3"
   tree = parse(code)
   phrase = get_units(tree)[0]
   score = get_scores(phrase)[0]
   assert score.data == "score"
   assert get_score_atoms(score) == ["talea", "3", "1", "in", "3"]


# ─── MULTIPLE UNITS ──────────────────────────────────────────────────────────

def test_multiple_units_count():
   code = "@vln·c d e f\n@pno·g a b c"
   tree = parse(code)
   assert len(get_units(tree)) == 2

def test_multiple_units_headers():
   code = "@vln·c d e f\n@pno·g a b c"
   tree = parse(code)
   units = get_units(tree)
   assert str(units[0].children[0].children[0]) == "vln"
   assert str(units[1].children[0].children[0]) == "pno"

def test_multiple_units_scores():
   code = "@vln·c d e f\n@pno·g a b c"
   tree = parse(code)
   units = get_units(tree)
   assert get_score_atoms(get_scores(units[0])[0]) == ["c", "d", "e", "f"]
   assert get_score_atoms(get_scores(units[1])[0]) == ["g", "a", "b", "c"]


# ─── MODIFIERS ───────────────────────────────────────────────────────────────

def test_dot_modifier():
   code = "@cordelia.mode·c d e"
   tree = parse(code)
   phrase = get_units(tree)[0]
   mods = get_modifiers(phrase)
   assert len(mods) == 1
   assert mods[0].children[0].data == "dot_mod"
   assert str(mods[0].children[0].children[0]) == "mode"

def test_colon_modifier():
   code = "@cordelia:tempo·c d e"
   tree = parse(code)
   phrase = get_units(tree)[0]
   mods = get_modifiers(phrase)
   assert len(mods) == 1
   assert mods[0].children[0].data == "colon_mod"
   assert str(mods[0].children[0].children[0]) == "tempo"

def test_dot_modifier_with_call():
   code = "@cordelia.mode(dorian)·c d e"
   tree = parse(code)
   phrase = get_units(tree)[0]
   mod = get_modifiers(phrase)[0].children[0]
   assert mod.data == "dot_mod"
   call = mod.children[1]
   assert call.data == "call"
   assert str(call.children[0].children[0].children[0]) == "dorian"

def test_colon_modifier_with_call():
   code = "@cordelia:tempo(120)·c d e"
   tree = parse(code)
   phrase = get_units(tree)[0]
   mod = get_modifiers(phrase)[0].children[0]
   assert mod.data == "colon_mod"
   call = mod.children[1]
   assert call.data == "call"
   assert str(call.children[0].children[0].children[0]) == "120"

def test_multiple_modifiers():
   code = "@cordelia.mode(dorian):tempo(120)·c d e"
   tree = parse(code)
   phrase = get_units(tree)[0]
   mods = get_modifiers(phrase)
   assert len(mods) == 2


# ─── MULTIPLE SCORES ─────────────────────────────────────────────────────────

def test_phrase_multiple_scores():
   code = "@cordelia·c d e·f g a"
   tree = parse(code)
   phrase = get_units(tree)[0]
   scores = get_scores(phrase)
   assert len(scores) == 2
   assert get_score_atoms(scores[0]) == ["c", "d", "e"]
   assert get_score_atoms(scores[1]) == ["f", "g", "a"]

def test_phrase_pipe_delimiter():
   code = "@cordelia·c d e|f g a"
   tree = parse(code)
   phrase = get_units(tree)[0]
   scores = get_scores(phrase)
   assert len(scores) == 2


# ─── SCORE ATOMS ─────────────────────────────────────────────────────────────

def test_score_atom_number():
   code = "@cordelia·3 1 2"
   tree = parse(code)
   phrase = get_units(tree)[0]
   atoms = get_score_atoms(get_scores(phrase)[0])
   assert atoms == ["3", "1", "2"]

def test_score_atom_negative_number():
   code = "@cordelia·-1 2 -3"
   tree = parse(code)
   phrase = get_units(tree)[0]
   atoms = get_score_atoms(get_scores(phrase)[0])
   assert atoms == ["-1", "2", "-3"]

def test_score_atom_symbol():
   code = "@cordelia·c # b"
   tree = parse(code)
   phrase = get_units(tree)[0]
   atoms = get_score_atoms(get_scores(phrase)[0])
   assert "#" in atoms
   assert "b" in atoms

def test_score_atom_braces():
   code = "@cordelia·{ c d e }"
   tree = parse(code)
   phrase = get_units(tree)[0]
   atoms = get_score_atoms(get_scores(phrase)[0])
   assert atoms[0] == "{"
   assert atoms[-1] == "}"


# ─── COMMENTS ────────────────────────────────────────────────────────────────

def test_comment_ignored():
   code = "; this is a comment\n@cordelia·c d e"
   tree = parse(code)
   assert len(get_units(tree)) == 1

def test_inline_comment_ignored():
   code = "@cordelia·c d e ; inline comment"
   tree = parse(code)
   phrase = get_units(tree)[0]
   atoms = get_score_atoms(get_scores(phrase)[0])
   assert atoms == ["c", "d", "e"]


# ─── INVALID INPUT ───────────────────────────────────────────────────────────

def test_invalid_missing_header():
   with pytest.raises(UnexpectedInput):
      parse("talea 3 1 in 3")

def test_invalid_empty():
   tree = parse("")
   assert tree.children == []

def test_invalid_only_comment():
   tree = parse("; just a comment")
   assert tree.children == []

# ─── COMPLEX ───────────────────────────────────────────────────────────

def test_complex():
	code = """

		@cordelia.lpf()
  :del():radio()·talea 3, 4 d#4 1 3# 4
  
@var 123
@var 123·@cordelia·talea 3 2

@cordelia
talea 3  2, 1 2 3
c4 fr dorian
wn qn
mf
zeus
@cordelia
talea 3  2, 1 2 3
c4 fr dorian
wn qn
mf
zeus

;comoment

@cordelia ;can i comment?
talea 3, 2, 4, {234, 3} in 4 

"""
	tree = parse(code)
	console.print(f"\nTREE:\n{tree.pretty(indent_str="\t")}")
	units = get_units(tree)
	check_types = [
		'phrase',
		'statement',
		'statement',
		'phrase',
		'phrase',
		'phrase',
		'phrase',
	]
	
	for i, unit in enumerate(units):
		assert unit.data == check_types[i]
 
