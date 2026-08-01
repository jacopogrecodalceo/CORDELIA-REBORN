import cordelia.path
from cordelia.console import console
from cordelia.registry import data

OUTPUT_DIR = cordelia.path.corpus / 'data'

TEMPLATE = '''
" File: ~/.config/nvim/syntax/cordelia_{section}.vim
" Reserved words for Cordelia — kept separate so this list can grow
" without touching the main syntax rules.

'''

for section in ['instrument', 'env', 'scala', 'mode', 'modifier']:
	strings = [f'syntax keyword cordelia_{section} {name}' for name in sorted(data[section])]
	words = '\n'.join(strings)
	output_path = OUTPUT_DIR / f'cordelia_{section}.vim'
	output_path.write_text(TEMPLATE + words)
	console.print(f'written @{output_path}')

section = 'func'
strings = [f'syntax keyword cordelia_{section} {path.stem}' for path in cordelia.path.func_corpus_dir.rglob('*.py') if not path.stem.startswith('_')]
words = '\n'.join(strings)
output_path = OUTPUT_DIR / f'cordelia_{section}.vim'
output_path.write_text(TEMPLATE + words)
console.print(f'written @{output_path}')

section = 'qualities'
strings = [f'syntax keyword cordelia_{section} {path.stem}' for path in cordelia.path.qualities_corpus_dir.rglob('*.py') if not path.stem.startswith('_')]
words = '\n'.join(strings)
output_path = OUTPUT_DIR / f'cordelia_{section}.vim'
output_path.write_text(TEMPLATE + words)
console.print(f'written @{output_path}')
