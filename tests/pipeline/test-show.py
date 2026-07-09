from cordelia.pipeline.parser import parse
from cordelia.pipeline.transformer import transform
from cordelia.console import console
from cordelia.models.ast import *
from cordelia.pipeline.resolver import resolve
code = r"""
@cordelia·talea {1 2 3} 16 in 8·osc{1 2x2}·alias 2? 1m·dur=2
"""
trees_parsed = parse(code)
console.print(f"\nPARSED TREES: {len(trees_parsed)}")
for t in trees_parsed:
	console.print(t)
	
trees = transform(trees_parsed)
console.print(f"\nTRANSFORMERs: {len(trees)}")
for t in trees:
	console.print(t)