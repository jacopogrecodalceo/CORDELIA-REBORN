import ctcsound

from cordelia.console import console
import cordelia.path
from config.options import CHANNELs, flags, init_settings
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
					devs.append(CSOUND_DEVICEs[kind][matches[0]])
					break
	return devs

def init():
	global CHANNELs
	get_devices()
	adc, dac = select_device()
	"""
	{'id': 'adc3', 'max_nchnls': 1}
	{'id': 'dac0', 'max_nchnls': 2}
	"""
	console.print(f'\n{adc}')
	console.print(f'\n{dac}')
	dac_nchnls = dac['max_nchnls']
	if CHANNELs > dac_nchnls:
		CHANNELs = dac_nchnls
		flags.append(f'--nchnls={CHANNELs}')
		
	flags.append(f'-o{dac['id']}')

def build_orchestra():
	orcs = init_settings
	orcs += [
		";"+"·"*64,
		"; BEGIN INCLUDES",
		cordelia.path.include.read_text(),
		"; END INCLUDES",
		";"+"·"*64,
	]

	return "\n".join(orcs)

