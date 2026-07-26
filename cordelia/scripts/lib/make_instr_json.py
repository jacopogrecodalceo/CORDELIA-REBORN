import json
import librosa
import numpy as np
from decimal import Decimal

import cordelia.path
from cordelia.console import console

INPUT_DIR = cordelia.path.instr_corpus_dir
OUTPUT_JSON = cordelia.path.instr_corpus_json

EXCLUDEs = ['__header']

instrs = {}

def add_orcs():
	for path in INPUT_DIR.rglob(f"*.orc"):
		name = path.stem
		if name in instrs:
			raise ValueError(f'DUPLICATE NAME: {name}')
		instrs[name] = {
			'kind': 'orc',
			'path': str(path)
		}



def anal_wav(path):
	audio, sr = librosa.load(path, sr=None)
	channels = audio.shape[0] if audio.ndim > 1 else 1
	f0 = librosa.yin(audio, fmin=25, fmax=3500)
	main_f0 = np.median(f0)
	return channels, sr, Decimal(main_f0)

def create_templates(sonvs_name):
	res = []
	for template_path in cordelia.path.sonvs_temp_corpus_dir.glob('*.j2'):
		variant = template_path.stem
		if variant not in EXCLUDEs:
			name = sonvs_name if variant == '_' else sonvs_name + variant
			res.append((name, variant))
	return res

def add_wavs():
	for path in INPUT_DIR.rglob(f"*.wav"):
		wav_name = path.stem
		channels, sr, main_f0 = anal_wav(path)
		for sonvs_name, template_stem in create_templates(wav_name):
			if sonvs_name in instrs:
				raise ValueError(f'DUPLICATE NAME: {sonvs_name} in {instrs}')
			instrs[sonvs_name] = {
				'kind': 'wav',
				'path': str(path),
				'template_stem': str(template_stem),
				'pitch': str(main_f0),
				'channels': channels,
				'sr': sr,
			}

def make_json():
	# Fixed: need to pass the data as second argument
	with open(OUTPUT_JSON, 'w') as f:
		json.dump(instrs, f, indent=3)  # Added indent for readability

add_orcs()
add_wavs()
make_json()

# Fixed: use the correct path
console.print(f'written @{OUTPUT_JSON}')