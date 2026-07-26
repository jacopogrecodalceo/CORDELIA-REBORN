from pathlib import Path
import struct
from decimal import Decimal
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
	return Decimal(10 ** (db / 20))


def fix_wav_header(path: Path) -> None:
	file_size = path.stat().st_size
	riff_size = file_size - 8
	data_size = file_size - 44

	with open(path, "r+b") as f:
		f.seek(4)
		f.write(struct.pack("<I", riff_size))
		f.seek(40)
		f.write(struct.pack("<I", data_size))

