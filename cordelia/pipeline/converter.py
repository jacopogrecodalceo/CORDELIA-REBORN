from loguru import logger
from cordelia.models.ast import Instrument
from cordelia.const import jinja_env, csound_comment_line
from cordelia.registry import ft_pool, orchestra_manager
from cordelia.registry import uid_tracker

from cordelia.const import jinja_env, csound_comment_line

def make_modifiers_chain(instrument):
	if not instrument.score['opcode']:
		return 'amain_out = amain_in'

def make_bridge(instrument):
	logger.debug('BRIDGE')
	chain = make_modifiers_chain(instrument)
	route_template = jinja_env.get_template('instr_bridge.j2')
	orcs = [
		csound_comment_line(f'BRIDGE {instrument.name}'),
		route_template.render(instrument=instrument, chain=chain)
	]
	return '\n'.join(orcs)

def _prepare_context(instrument: Instrument) -> None:
	instrument.ft_num = {q: ft_pool.alloc() for q in instrument.score}

def convert(instrument: Instrument) -> None:
	if not isinstance(instrument, Instrument):
		return
	if instrument.uid in uid_tracker:
		orc_lines = [csound_comment_line('UPDATE')]
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
				if quality_name == 'cycle':
					string = f'gk{ instrument.uid }_cycle init { instrument.score['cycle'] }'
				elif quality_name in ['talea', 'colores', 'dur', 'dyn', 'env', 'space']:
					string = f'gi{original_instrument.uid}_{quality_name} ftgen {original_instrument.ft_num[quality_name]}, 0, giFTGEN_SIZE, -2, {len(values)}, {", ".join(map(str, values))}'

				orc_lines.append(string)
				logger.debug(orc_lines)
		orc = '\n'.join(orc_lines)
	else:
		logger.info(f'rendering born | id={instrument.instr_id} | name={instrument.name}')
		template = jinja_env.get_template('instrument_born.j2')
		_prepare_context(instrument)
		orc = template.render(instrument=instrument)
		instrument.state = False
		uid_tracker[instrument.uid] = instrument
		orchestra_manager.put('instrument', make_bridge(instrument))

	orchestra_manager.put('score', orc)