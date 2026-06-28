from loguru import logger
from numpy import full
import cordelia.pipeline.processor.instrument.name
import cordelia.pipeline.processor.instrument.modifiers
import cordelia.pipeline.processor.instrument.score
from cordelia.pipeline.transformer import Instrument, Variable
from cordelia.registry import tracker, orchestra_manager

def process(unit: Instrument | Variable):
	if isinstance(unit, Instrument):
	
		# NAME
		instrument = unit
		instrument.uid = f'{instrument.name}_{instrument.instr_id}'

		# validate in cordelia
		assert cordelia.pipeline.processor.instrument.name.validate(instrument.name), 'INSTR NAME not FOUND'


		if instrument.name not in tracker['instrument']:
			full_instr_orc = cordelia.pipeline.processor.instrument.name.load(instrument.name)
			orchestra_manager.put('instrument', full_instr_orc)
			tracker['instrument'].add(instrument.name)


		# put it in the queue to send immediately to csound if not already sent
		# store in the queue of the sent modifiers

		# MOD
		for mod in instrument.modifiers:
			if mod:
				assert cordelia.pipeline.processor.instrument.modifiers.validate(mod.name), 'MOD not FOUND'

			if mod.name not in tracker['modifier']:
				full_opcode_orc = cordelia.pipeline.processor.instrument.modifiers.load(mod.name)
				orchestra_manager.put('modifier', full_opcode_orc)
				tracker['modifier'].add(instrument.name)
			# put it in the queue to send immediately to csound if not already sent
			# store in the queue of the sent modifiers

		# SCORE
		# deduct the quality
		logger.debug(instrument.qualities)
		for q in instrument.qualities:
			logger.debug(f"{q} is going to be deducted")
			cordelia.pipeline.processor.instrument.score.deduce_quality(q, instrument)

		assert hasattr(instrument, 'score'), instrument
		logger.debug(instrument.score)
	elif isinstance(unit, Variable):
		pass
	else:
		raise ValueError('problem class of the unit is not recognised')