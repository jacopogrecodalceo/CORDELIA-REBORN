from __future__ import annotations
from datetime import datetime 
from pythonosc.udp_client import SimpleUDPClient

from cordelia.helpers import IndexedData, calculate_cordelia_age
import cordelia.path

data = IndexedData(cordelia.path.json)

year = calculate_cordelia_age()['years']
DATE = datetime.today().strftime(f'{year}%m%d-%H%M')

OUTPUT_SCORE_NAME = f'cor{DATE}'
OUTPUT_SCORE_PATH = cordelia.path.score / OUTPUT_SCORE_NAME

QUERY_CSOUND_WHILE_SLEEP_TIME = 1/12 #the sleep time in the main while loop

CSOUND_QUALITY_FTGEN_SIZE = 4096 #the size of the ft of qualities

CSOUND_DEVICEs = {
   'adc': {},
   'dac': {}
}

QUERY_UDP_SLEEP_TIME = 1/8

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