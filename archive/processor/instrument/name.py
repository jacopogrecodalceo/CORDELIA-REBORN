from pathlib import Path
from loguru import logger
from cordelia.const import data, jinja_env, csound_comment_line


def validate(name: str):
	logger.debug(f'checking {name} in data names')
	if name in data['instrument']:
		return True
	return False
 
def make_instr_prerouting(name):
	route_template = jinja_env.get_template('instrument_prerouting.j2')
	orc = route_template.render(name=name)
	return orc

def load(name: str):
	logger.debug(f'loading {name}..')
	path = Path(data['instrument'][name])
	orc = [
    	csound_comment_line(f'ROUTING {name}'), 
		make_instr_prerouting(name),
		csound_comment_line(f'INSTRUMENT {name} LOADED'), 
		path.read_text()
   ]
	return '\n'.join(orc)
