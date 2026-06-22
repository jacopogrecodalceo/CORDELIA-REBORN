import cordelia.const

CHANNELs = 2
SR = 48000
KSMPS = 64
CONTROL_CHANNELs = []

if CHANNELs == 4:
   CHANNEL_MAP = [1, 2, 4, 3]
else:
   CHANNEL_MAP = [ch for ch in range(CHANNELs)]

flags = [
   #f'-o{cordelia.const.OUTPUT_SCORE_PATH}',
   f'--nchnls={CHANNELs}',
   f'--sample-rate={SR}',
   '--format=24bit',
   f'--ksmps={KSMPS}',
   '--0dbfs=1',
   
   '--m-amps=1',
   '--m-range=1',
   '--m-warnings=0',
   '--m-dB=1',
   '--m-colours=1',
   '--m-benchmarks=0',
   
   '-m2', #rtevent
   
   "-+id_artist=jacopo greco d'alceo",
]



