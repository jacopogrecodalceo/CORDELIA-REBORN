from pathlib import Path
from loguru import logger
from cordelia.const import data

def validate(name: str):
	logger.debug(f'checking {name} in data mods')
	if name in data['mod']:
		return True
	return False

def load(name: str):
	logger.debug(f'loading {name}..')
	path = Path(data['mod'][name])
	return path.read_text()