from cordelia.pipeline.parser import parse
from cordelia.pipeline.transformer import transform
from cordelia.console import console

code = r"""
@tiny.dioa{50+osc{50 2}}:dio{40*3*2 2}·talea {1 2 3} 16 in 8·osc{1 2^2}·alias -2^12 cls^2

@tiny.dio{50+osc{50 2^12}}:dio{40*3*2 2}·dorian 1 3 5 7m^3

@statement 2+osc{3 2 lear}+osc{3 -23 giasine}

@tiny·talea {1 2 3} 16 in 8·osc{1 2}

@var osc{tst}
"""
poems = parse(code)
for poem in poems:
#	console.print(poem)
	poem = transform(poem)
	console.print(poem)
	console.print('-'*128)

