import pytest
from cordelia.pipeline.lexer import lex


# ─── SINGLE UNIT ─────────────────────────────────────────────────────────────

def test_single_inline_phrase():
   assert lex("@cordelia·talea 3 1") == ["@cordelia·talea 3 1"]

def test_single_statement():
   assert lex("@var 123") == ["@var 123"]

def test_single_multiline_phrase():
   src = "@cordelia\ntalea 3 1\nc4 dorian"
   assert lex(src) == ["@cordelia\ntalea 3 1\nc4 dorian"]


# ─── MULTIPLE UNITS ──────────────────────────────────────────────────────────

def test_multiple_inline():
   src = "@vln·c d e·@pno·g a b"
   result = lex(src)
   assert len(result) == 2
   assert result[0] == "@vln·c d e·"
   assert result[1] == "@pno·g a b"

def test_multiple_inline_newline_separated():
   src = "@vln·c d e f\n@pno·g a b c"
   result = lex(src)
   assert len(result) == 2
   assert result[0] == "@vln·c d e f"
   assert result[1] == "@pno·g a b c"

def test_multiple_multiline():
   src = "@cordelia\ntalea 3 1\n@var 123"
   result = lex(src)
   assert len(result) == 2
   assert result[0] == "@cordelia\ntalea 3 1"
   assert result[1] == "@var 123"


# ─── BLANK LINES ─────────────────────────────────────────────────────────────

def test_blank_lines_stripped():
   src = "@cordelia\n\ntalea 3 1\n\nc4 dorian"
   assert lex(src) == ["@cordelia\ntalea 3 1\nc4 dorian"]

def test_leading_blank_lines_stripped():
   src = "\n\n@cordelia·talea 3 1"
   assert lex(src) == ["@cordelia·talea 3 1"]

def test_trailing_blank_lines_stripped():
   src = "@cordelia·talea 3 1\n\n"
   assert lex(src) == ["@cordelia·talea 3 1"]

def test_blank_lines_between_units_stripped():
   src = "@vln·c d e\n\n\n@pno·g a b"
   result = lex(src)
   assert len(result) == 2


# ─── COMMENTS ────────────────────────────────────────────────────────────────

def test_comment_stripped():
   src = "; full line comment\n@cordelia·talea 3 1"
   assert lex(src) == ["@cordelia·talea 3 1"]

def test_inline_comment_stripped():
   src = "@cordelia·talea 3 1 ; inline"
   assert lex(src) == ["@cordelia·talea 3 1"]

def test_comment_between_units():
   src = """@vln·c d e
   ; comment
@pno·g a b"""
   result = lex(src)
   assert len(result) == 2

def test_comment_only():
   assert lex("; just a comment") == []


# ─── EDGE CASES ──────────────────────────────────────────────────────────────

def test_empty_source():
   assert lex("") == []

def test_whitespace_only():
   assert lex("   \n\t\n  ") == []

def test_no_at_sign():
   assert lex("talea 3 1") == []

def test_preserves_delimiters():
   src = "@cordelia·talea 3 1·c4 dorian·wn qn"
   assert lex(src) == ["@cordelia·talea 3 1·c4 dorian·wn qn"]

def test_preserves_modifiers():
   src = "@cordelia.lpf:tempo(120)·talea 3 1"
   assert lex(src) == ["@cordelia.lpf:tempo(120)·talea 3 1"]

def test_multiline_modifiers():
   src = "@cordelia.lpf\n:del()·talea 3 1"
   assert lex(src) == ["@cordelia.lpf\n:del()·talea 3 1"]

def test_complex():
	code = r"""@cordelia.lpf
	:del()
	:radio
	talea 4 d#4 1 3# 4

	@var 123
	@var 123

	@cordelia·talea {3 1 -1} 2 in 3/4 and talea 3 2 in 4/4·f lydian 1 2 3 4·d <1 3m 5>
	mf<f in 4·cls hyd

	@cordelia
	talea 3 2 1 2 3
	c4 fr dorian
	wn qn
	mf
	zeus

	;comment

	@cordelia ;can i comment?
	talea 3 2 4 {234 3} in 4"""
	assert len(lex(code)) == 6