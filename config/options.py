from cordelia.const import FTGEN_SIZE, TALEA_RESAMPLE_LEN
import cordelia.path 

CHANNELs = 2
CSOUND_nchnls = 2
OFF_CHANNEL = 0

SR = 48000
KSMPS = 64
CONTROL_CHANNELs = []

if CHANNELs == 4:
   CHANNEL_MAP = [1, 2, 4, 3]
else:
   CHANNEL_MAP = [ch for ch in range(CHANNELs)]

flags = [
   #f'-o{cordelia.const.OUTPUT_SCORE_PATH}',
   f'--nchnls={CSOUND_nchnls}',
   f'--sample-rate={SR}',
   f'--ksmps={KSMPS}',
   '--format=24bit',

   '--0dbfs=1',

   '-d', # hide ftgen ascii tables

   '--m-amps=1',
   '--m-range=1',
   '--m-warnings=0',
   '--m-dB=1',
   '--m-colours=1',
   '--m-benchmarks=0',
   
   '-m2', # hide rtevent
   
   f'--env:INCDIR={str(cordelia.path.csound / 'orc')}',
   f'--env:SSDIR={str(cordelia.path.instr_corpus_dir)}',
   
   "-+id_artist=jacopo greco d'alceo",
]

init_settings = [
   "; BEGIN CORDELIA SETTINGS",

   f"ginchnls init {CHANNELs}",
   f"giCHs init {CHANNELs}",
   f"giOFF_CH init {OFF_CHANNEL}",
   
   "gimainclock_ch init 0",
   "giquarterclock_ch init 0",
   "giINSTR_CLEAR_COUNT init 0",

   f"giTALEA_RESAMPLE_LEN init {TALEA_RESAMPLE_LEN}",
   f"giFTGEN_SIZE init {FTGEN_SIZE}",

   "; END CORDELIA SETTINGS",

]

