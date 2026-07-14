from cordelia.pipeline.parser import parse
from cordelia.pipeline.transformer import transform
from cordelia.pipeline.deducer import deduce
from cordelia.pipeline.comparer import compare
from cordelia.pipeline.learner import learn
from cordelia.pipeline.converter import offer

code = r"""
@tiny·eu 3 8 in 8·talea 1 3 -8 in 4·dorian c.. 1 3 5

"""
pending_poems = []
for line in parse(code):
	poem = transform(line)
	deduce(poem)
	poem.process()
	pending_poems.append(poem)
session_poems = compare(pending_poems)
learn(session_poems)
offer(session_poems)
print(session_poems)

