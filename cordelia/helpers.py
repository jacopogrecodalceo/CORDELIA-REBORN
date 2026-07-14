
from datetime import date
from dateutil.relativedelta import relativedelta

def calculate_cordelia_age() -> dict:
	today = date.today()
	delta = relativedelta(today, date(1989, 10, 11))
	
	return {
		'years': delta.years,
		'months': delta.months,
		'days': delta.days
	}

def db_to_amplitude(db):
	"""Convert dB to amplitude ratio (0-1)."""
	return 10 ** (db / 20)

