from corpus.func import *

def main(args):
	items = args.items
	if len(items) == 3:
		values   = items[:2]
		waveform = items[2]
		if not waveform.isalpha():
			raise CorpusError(f'{__name__} {waveform} not a waveform')
	elif len(items) == 2:
		values   = items[:2]
		waveform = 'giasine'
	else:
		raise CorpusError(f'{__name__} error in parameters length')

	packed = values + [waveform]
	if len(packed) != 3:
		raise CorpusError(f'{__name__} {packed} not enough values')

	return f"oscil3:k({', '.join(packed)})"