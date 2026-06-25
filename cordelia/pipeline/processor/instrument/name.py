from loguru import logger
from cordelia.const import data
import cordelia.session.instrument_tracker as instrument_tracker

def validate(name: str):
	logger.debug(f'checking {name} in data names')
	if name in data.instruments:
		return True
	return False

def has_unique_id(name_id: str):
	if instrument_tracker.has(name_id):
		return False
	instrument_tracker.add(name_id)
	logger.debug(f'{name_id} added to list')
	return True