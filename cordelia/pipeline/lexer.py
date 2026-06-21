from __future__ import annotations
import re


_COMMENT = re.compile(r";[^\n]*")


def _strip_comments(source: str) -> str:
	return _COMMENT.sub("", source)


def _strip_blank_lines(chunk: str) -> str:
	lines = [l for l in chunk.splitlines() if l.strip()]
	return "\n".join(lines)


def lex(source: str) -> list[str]:
	source = _strip_comments(source)
	raw = re.split(r"(?=@)", source)
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