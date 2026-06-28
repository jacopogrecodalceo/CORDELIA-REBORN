from loguru import logger
from cordelia.console import console
from cordelia.models.transformers import Array
from cordelia.pipeline.transformer import Instrument, Variable
from cordelia.const import data_to_know
from cordelia.registry import orchestra_manager
from cordelia.registry import tracker

def count_talea(instrument: Instrument):
	count = 1
	for i, v in enumerate(instrument.score['talea']):
		if int(v) > 0:
			instrument.score['talea'][i] = count
			count += 1
	logger.debug(instrument.score['talea'])

def load_known_instrument_qualities(instrument: Instrument):
	score_tokens = (
		token
		for token_list in instrument.score.values()
		for entry in token_list
		for token in (entry.items if isinstance(entry, Array) else [entry])
	)

	for token in score_tokens:
		for quality_name, keyword_path_map in data_to_know.items():
			if token in keyword_path_map:
				is_named_token = any(c.isalpha() for c in token)
				if is_named_token and token not in tracker[quality_name]:
					with open(keyword_path_map[token]) as f:
						orchestra_manager.put(quality_name, f.read())
					tracker[quality_name].add(token)
					
def eval_dur(instrument: Instrument):
	
	def make_durs_from_talea(talea):
		result = []
		count = 1
		for x in reversed(talea):
			if x == 0:
				count += 1
			else:
				result.append(count)
				count = 1
		result = list(reversed(result))
		result[-1] += count-1
		return result
	
	deducted_durs = instrument.score['dur']
	if not instrument.score.get('talea', False):
		raise ValueError(f'Error in post processor {instrument.score = }')
	talea_durs = make_durs_from_talea(instrument.score['talea'])
	
	logger.debug(f'these are the duration from cordelia code {deducted_durs}')
	if 'dur' in deducted_durs:
		# this means there's an operation to do
		index_dur = deducted_durs.index('dur')
		op_value = deducted_durs[index_dur+1]
		dur_values = deducted_durs[index_dur+2:]
		if isinstance(dur_values[0], Array):
			dur_values = dur_values[0].items
		
		logger.debug(f"there's dur so operator {op_value} will evaluate {dur_values}")
		logger.debug(f"talea dur is {talea_durs}")
		if op_value == '=':
			instrument.score['dur'] = dur_values
		else:	
			eval_durs = []
			for i, talea_dur in enumerate(talea_durs):
				eval_string = f'{talea_dur}{op_value}{dur_values[i%len(dur_values)]}'
				eval_dur = eval(eval_string)
				eval_durs.append(eval_dur)
			instrument.score['dur'] = eval_durs
	else:
		instrument.score['dur'] = talea_durs

def convert_dyn(instrument: Instrument):
	for i, value in enumerate(instrument.score['dyn']):
		#instrument.score['dyn'][i] = data.file('dyns')[value]['norm']
		instrument.score['dyn'][i] = rf'${value}'

def prepare_env(instrument: Instrument):
	for i, value in enumerate(instrument.score['env']):
		instrument.score['env'][i] = f'gi{value}'

def run(unit: Instrument | Variable):
	if not isinstance(unit, Instrument):
		return

	instrument = unit

	load_known_instrument_qualities(instrument)
	eval_dur(instrument)
	convert_dyn(instrument)
	prepare_env(instrument)
	count_talea(instrument)

