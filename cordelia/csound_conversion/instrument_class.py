from loguru import logger
from jinja2 import Environment, FileSystemLoader
from cordelia.models.transformers import Instrument
from cordelia.const import FTGEN_SIZE, jinja_env
from cordelia.registry import ft_pool, orchestra_manager
from cordelia.registry import uid_tracker


def _prepare_context(instrument: Instrument) -> None:
	instrument.ft_num = {q: ft_pool.alloc() for q in instrument.score}

def convert(instrument: Instrument) -> None:
	if not isinstance(instrument, Instrument):
		return
	if instrument.uid in uid_tracker:
		orc_lines = ['; UPDATE\n']
		logger.debug(f'{instrument.uid} is in uid_tracker')

		# check if has some changement or anything else
		original_instrument = uid_tracker[instrument.uid]
		logger.debug(f'PREV: {original_instrument}—{original_instrument.score}')
		logger.debug(f'ACTUAL: {instrument}—{instrument.score}')

		for quality_name, values in instrument.score.items():
			logger.debug(f'COMPARING: {quality_name}')
			prev_values = original_instrument.score.get(quality_name)
			if prev_values == values:
				logger.debug(f'{quality_name} is the same as before')
				logger.info(f'skip | id={instrument.instr_id} | name={instrument.name}')
				instrument.state = 'skip'
			else:
				logger.debug(f'{quality_name}: previous {prev_values} is different from {values}')
				original_instrument.state = 'patch'
				original_instrument.score[quality_name] = values
				logger.info(f'updating | id={original_instrument.instr_id} | name={original_instrument.name}')
				logger.debug(values)
				string = f'gi{original_instrument.uid}_{quality_name} ftgen {original_instrument.ft_num[quality_name]}, 0, {FTGEN_SIZE}, -2, {len(values)}, {", ".join(map(str, values))}'
				orc_lines.append(string)
				logger.debug(orc_lines)
		orc = '\n'.join(orc_lines)
	else:
		logger.info(f'rendering born | id={instrument.instr_id} | name={instrument.name}')
		template = jinja_env.get_template('instrument_born.j2')
		_prepare_context(instrument)
		orc = template.render(instrument=instrument, FTGEN_SIZE=FTGEN_SIZE)
		instrument.state = False
		uid_tracker[instrument.uid] = instrument


	orchestra_manager.put('score', orc)