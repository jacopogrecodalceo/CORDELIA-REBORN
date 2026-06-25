import cordelia.pipeline.processor.instrument.name
import cordelia.pipeline.processor.instrument.modifiers
import cordelia.pipeline.processor.instrument.score
from cordelia.pipeline.transformer import Instrument, Variable
def process(unit: Instrument | Variable):
	if isinstance(unit, Instrument):
    
		# NAME
		instrument = unit
		assert cordelia.pipeline.processor.instrument.name.validate(instrument.name), 'INSTR NAME not FOUND'
		assert cordelia.pipeline.processor.instrument.name.has_unique_id(f'{instrument.name}#{instrument.id}'), 'INSTRUMENT NAME AND ID ALREADY IN USE!'
		# put it in the queue to send immediately to csound if not already sent
		# store in the queue of the sent modifiers

		# MOD
		for mod in instrument.modifiers:
			if mod:
				assert cordelia.pipeline.processor.instrument.modifiers.validate(mod.name), 'MOD not FOUND'
			full_opcode_orc = cordelia.pipeline.processor.instrument.modifiers.load(mod.name)

			# put it in the queue to send immediately to csound if not already sent
			# store in the queue of the sent modifiers

		# SCORE
		# deduct the quality
		for q in instrument.score:
			print(cordelia.pipeline.processor.instrument.score.deduce_quality(q))
		# fill missing quality

	elif isinstance(unit, Variable):
		pass
	else:
		raise ValueError('problem class of the unit is not recognised')