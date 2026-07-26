from __future__ import annotations
from pathlib import Path
from datetime import datetime 
from jinja2 import Environment, FileSystemLoader
import abjad

from cordelia.helpers import calculate_cordelia_age
import cordelia.path

year = calculate_cordelia_age()['years']
DATE = datetime.today().strftime(f'{year}%m%d·%H%M')

OUTPUT_SCORE_NAME = f'cor{DATE}'

OUTPUT_SCORE_DIR = cordelia.path.main_dir / 'score' / f'cor{DATE}'
Path(OUTPUT_SCORE_DIR).mkdir(parents=True, exist_ok=True)
OUTPUT_SCORE_PATH = OUTPUT_SCORE_DIR / f'{OUTPUT_SCORE_NAME}.wav' 

QUERY_UDP_WHILE_SLEEP_TIME = 1/8
QUERY_CSOUND_WHILE_SLEEP_TIME = 1/12		# the sleep time in the main while loop
SHORT_REST_AFTER_INIT = 1/4					# sec after csound init

CSOUND_DEVICEs = {
	'adc': {},
	'dac': {}
}

CLEAR_INSTRUMENT_NUM = 950
FTGEN_SIZE = 8192

CYCLE_TARGET_DURATION = abjad.Duration(64, 4)

TALEA_RESAMPLE_LEN = 512

UDP_SIZE = 8192

UDP_PORTs = {
	10015: "CORDELIA",
	10000: "CSOUND",
	10025: "REAPER",
}

JINJA_CSOUND_EMIT_ENV = Environment(
	loader=FileSystemLoader(cordelia.path.templates),
	trim_blocks=True,
	lstrip_blocks=True,
)

JINJA_SONVS_TEMPLATE_ENV = Environment(
	loader=FileSystemLoader(cordelia.path.sonvs_temp_corpus_dir),
	trim_blocks=True,
	lstrip_blocks=True,
)

def csound_comment_line(string):
	return f'\n; ' + string + '·'*128
