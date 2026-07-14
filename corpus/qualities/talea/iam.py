import re
import nltk
from cordelia.console import console

"""Check if cmudict is downloaded, download if needed."""
""" try:
	nltk.data.find('corpora/cmudict.zip')
except LookupError:
	nltk.download("cmudict", quiet=True) """
from nltk.corpus import cmudict
from corpus.qualities.talea import *

cmu = cmudict.dict()
VOWELS = set("aeiou")

IAMBIC = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]

def _guess_syllable_count(word: str) -> int:
	count, prev_vowel = 0, False
	for ch in word.lower():
		is_vowel = ch in VOWELS
		if is_vowel and not prev_vowel:
			count += 1
		prev_vowel = is_vowel
	return max(1, count)


def _word_stress(word: str) -> tuple[list[int | None], int]:
	"""
	Returns (stresses, syllable_count).
	None means the syllable is free (monosyllable or unknown).
	"""
	key = word.lower().strip(".,;:!?\"'")
	if key in cmu:
		phones = cmu[key][0]
		stresses = [
			int(ph[-1]) > 0
			for ph in phones
			if ph[-1].isdigit()
		]
		count = len(stresses)
		if count == 1:
			return [None], 1   # monosyllable: free
		return stresses, count
	count = _guess_syllable_count(key)
	return [None] * count, count  # unknown: all free


def _fit_iambic(syllables: list[int | None], template: list[int] = IAMBIC) -> tuple[list[int], float]:
	"""
	DP fit: free syllables (None) can be 0 or 1.
	Fixed syllables stay as-is.
	Minimizes hamming distance to template.
	"""
	n = len(syllables)
	t = len(template)
	# dp[i] = min cost up to syllable i, with chosen values
	# we pad or trim template to match n
	tpl = (template * ((n // t) + 1))[:n]

	result = []
	for i, s in enumerate(syllables):
		if s is None:
			result.append(tpl[i])   # free: just follow template
		else:
			result.append(1 if s else 0)  # fixed

	matches = sum(r == tpl[i] for i, r in enumerate(result))
	score = matches / n if n > 0 else 0.0
	return result, score

def match(items: list) -> bool:
   return False

def main(verse: str) -> tuple[list[int], float]:
	words = re.findall(r"[a-zA-Z']+", verse)
	syllables = []
	for w in words:
		stresses, _ = _word_stress(w)
		syllables.extend(stresses)
	result, score = _fit_iambic(syllables)
	console.print(f'for [field]{verse}[/field]')
	console.print(f'[success]{result}[/success]')
	console.print(f'score: [success]{score}[/success]')
	return result

if __name__ == '__main__':
	verse = "do not cry until the sad river flows"
	res = main(verse) 
	print(res)