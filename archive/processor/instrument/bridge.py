from loguru import logger
from cordelia.const import jinja_env, csound_comment_line

def make_modifiers_chain(instrument):
	if not instrument.score['opcode']:
		return 'amain_out = amain_in'

def make(instrument):
	logger.debug('BRIDGE')
	chain = make_modifiers_chain(instrument)
	route_template = jinja_env.get_template('instr_bridge.j2')
	orcs = [
		csound_comment_line(f'BRIDGE {instrument.name}'),
		route_template.render(instrument=instrument, chain=chain)
	]
	return '\n'.join(orcs)