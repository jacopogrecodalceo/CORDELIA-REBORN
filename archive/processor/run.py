from loguru import logger
import archive.processor.instrument.name
import archive.processor.instrument.score
from cordelia.pipeline.transformer import Instrument, Variable
from cordelia.registry import tracker, orchestra_manager
from cordelia.csound_conversion import opcode

def process(unit: Instrument | Variable):
	if isinstance(unit, Instrument):
	
		# NAME
		instrument = unit
		instrument.uid = f'{instrument.name}_{instrument.instr_id}'

		# validate in cordelia
		assert archive.processor.instrument.name.validate(instrument.name), 'INSTR NAME not FOUND'

		if instrument.name not in tracker['instrument']:
			full_instr_orc = archive.processor.instrument.name.load(instrument.name)
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
				opcode_class = opcode.parse(full_opcode_orc)
				orchestra_manager.put('modifier', full_opcode_orc)
				tracker['modifier'][mod.name] = opcode_class

			instrument.score['opcode'].append(tracker['modifier'][mod.name])

			# put it in the queue to send immediately to csound if not already sent
			# store in the queue of the sent modifiers
		

		# SCORE
		# deduct the quality
		logger.debug(instrument.qualities)
		for q in instrument.qualities:
			logger.debug(f"{q} is going to be deducted")
			archive.processor.instrument.score.deduce_quality(q, instrument)

		assert hasattr(instrument, 'score'), instrument
		logger.debug(instrument.score)
	elif isinstance(unit, Variable):
		pass
	else:
		raise ValueError('problem class of the unit is not recognised')