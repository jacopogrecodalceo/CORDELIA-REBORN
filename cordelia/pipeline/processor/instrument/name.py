from pathlib import Path
from loguru import logger
from cordelia.const import data, jinja_env


def validate(name: str):
	logger.debug(f'checking {name} in data names')
	if name in data['instrument']:
		return True
	return False
 
def load(name: str):
	logger.debug(f'loading {name}..')
	path = Path(data['instrument'][name])
	instr_orc = path.read_text()

	route_template = jinja_env.get_template('instrument_post.j2')
	instr_orc += f'\n; ··· ROUTING {name}\n'
	instr_orc += route_template.render(name=name)
	""" src, _, _ = jinja_env.loader.get_source(jinja_env, 'instrument_post.j2')
	logger.debug(src)
	logger.debug(instr_orc) """
	return instr_orc
