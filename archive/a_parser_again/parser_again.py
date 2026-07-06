import re
from lark import Lark, Transformer, v_args
from pathlib import Path

GRAMMAR_PATH = Path(__file__).parent / "main.lark"

def _strip_blank_lines(chunk: str) -> str:
	lines = [l for l in chunk.splitlines() if l.strip()]
	return "\n".join(lines)

_AT = re.compile(r"(?=@)")

def lex(source: str) -> list[str]:
	#source = _strip_comments(source)
	raw = re.split(_AT, source)
	chunks = []
	for chunk in raw:
		chunk = chunk.strip()
		# remove all unnecessary
		if not chunk or not chunk.startswith("@"):
			continue
		chunk = _strip_blank_lines(chunk)
		if chunk:
			chunks.append(chunk)
	return chunks

p = Lark(GRAMMAR_PATH.read_text(), start="unit", parser="earley", ambiguity="resolve")

def parse(source: str) -> list:
	return [p.parse(chunk) for chunk in lex(source)]
# ============================================
# USAGE EXAMPLE
# ============================================

if __name__ == "__main__":	
	# Test with your examples
	code = r"""
@aaron.lpf{}.radio{osc{1 2 3}}·eu 3 8 in 8·dorian d' d. 1 2x2 3 9x9·mf f·cls x2

@var 12+osc{lf{1 2} 4}

@aaronx2·12+osc{lf{1 2} 4}·excx2 x2
"""
	
	trees = parse(code)
	for t in trees:
		print(t.pretty())