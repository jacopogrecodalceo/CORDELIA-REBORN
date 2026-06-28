from __future__ import annotations
from datetime import datetime 
from pythonosc.udp_client import SimpleUDPClient
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import orjson
from loguru import logger

from cordelia.helpers import calculate_cordelia_age
import cordelia.path

year = calculate_cordelia_age()['years']
DATE = datetime.today().strftime(f'{year}%m%d-%H%M')

OUTPUT_SCORE_NAME = f'cor{DATE}'
OUTPUT_SCORE_PATH = cordelia.path.score / OUTPUT_SCORE_NAME

QUERY_UDP_WHILE_SLEEP_TIME = 1/8
QUERY_CSOUND_WHILE_SLEEP_TIME = 1/12 #the sleep time in the main while loop
SHORT_REST_AFTER_INIT = 1/4 #sec after csound init
CSOUND_QUALITY_FTGEN_SIZE = 4096 #the size of the ft of qualities

CSOUND_DEVICEs = {
	'adc': {},
	'dac': {}
}

FTGEN_SIZE = 8192

REAPER_CLIENT = SimpleUDPClient(
	"127.0.0.1",
	8500,
)

UDP_SIZE = 4096

UDP_PORTS = {
	10015: "CORDELIA",
	10000: "CSOUND",
	10025: "REAPER",
}

jinja_env = Environment(
	loader=FileSystemLoader(cordelia.path.templates),
	trim_blocks=True,
	lstrip_blocks=True,
)

data = {
	f.stem: orjson.loads(f.read_bytes())
	for f in cordelia.path.json.glob("*.json")
}

data_to_know = {k: v for k, v in data.items() if k not in {'dyn', 'dur', 'mode'}}