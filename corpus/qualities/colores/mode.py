from __future__ import annotations
from cordelia.pipeline.transformer import Quality
from cordelia.data import data

def mode(quality: Quality) -> tuple[str, Quality] | None:
	if not quality.items or quality.items[0] in data.modes:
		return None
	return "colores", Quality(items=quality.items[1:])

if __name__ == '__main__':
	verse = "dorian"
	res = mode(verse) 
	print(res)