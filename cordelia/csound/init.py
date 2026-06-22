import ctcsound

import cordelia.path
from cordelia.console import console
from config.options import CHANNELs, flags
from cordelia.const import CSOUND_DEVICEs

from cordelia.csound.helpers import organise_devs

def get_devices():
	cs = ctcsound.Csound()
	cs.setOption('-n')
	cs.createMessageBuffer(False)  # False = don't print to stdout/stderr 
	cs.start()
	CSOUND_DEVICEs['adc'] = organise_devs(cs.audioDevList(False))
	CSOUND_DEVICEs['dac'] = organise_devs(cs.audioDevList(True))
	cs.stop()

def select_device():
	devs = []
	for kind, path in [
		('adc', cordelia.path.adc_dev_list),
		('dac', cordelia.path.dac_dev_list),
	]:
		dev_list = list(CSOUND_DEVICEs[kind].keys())
		with open(path, 'r') as f:
			for line in f.readlines():
				if line.startswith(';'):
					continue
				line = line.strip().split()
				eventually_flags = line[1:] if len(line) > 1 else None
				if eventually_flags:
					flags.extend(eventually_flags)
				matches = [d for d in dev_list if line[0] in d]
				if matches:
					devs.append((kind, CSOUND_DEVICEs[kind][matches[0]]))
					break
	return devs

if __name__ == "__main__":
	get_devices()
	adc, dac = select_device()
	dac_nchnls = dac[1]['max_nchnls']
	if CHANNELs > dac_nchnls:
		CHANNELs = dac_nchnls
		flags.append(f'--nchnls={CHANNELs}')

	#ctcsound.csoundInitialize(ctcsound.CSOUNDINIT_NO_ATEXIT | ctcsound.CSOUNDINIT_NO_SIGNAL_HANDLER)
	csound_cordelia = ctcsound.Csound()
	console.print("CORDELIA's FLAGs")
	for f in flags:
		console.print(f'\t{f}')
		csound_cordelia.setOption(f)
