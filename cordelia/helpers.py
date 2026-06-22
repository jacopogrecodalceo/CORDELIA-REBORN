from collections import defaultdict
from pathlib import Path
from typing import Any
import orjson
from loguru import logger

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

class IndexedData:
	def __init__(self, path: Path) -> None:
		self._data: dict[str, dict[str, Any]] = {}
		self._index: defaultdict[str, list[tuple[str, Any]]] = defaultdict(list)
		self._load(path)

	def _load(self, path: Path) -> None:
		for file in path.glob("*.json"):
			name = file.stem
			try:
				raw = orjson.loads(file.read_bytes())
			except Exception as e:
				logger.warning(f"data | skipping {file.name}: {e}")
				continue
			self._data[name] = raw
			for key, val in raw.items():
				self._index[key].append((name, val))
			logger.debug(f"data | loaded {name} ({len(raw)} keys)")

	def __contains__(self, key: str) -> bool:
		return key in self._index

	def __getitem__(self, key: str) -> list[tuple[str, Any]]:
		if key not in self._index:
			raise KeyError(key)
		return self._index[key]

	def get(self, key: str, default: Any = None) -> list[tuple[str, Any]] | None:
		return self._index.get(key, default)

	def has_key_in(self, name: str, key: str) -> bool:
		return name in self._data and key in self._data[name]

	def keys_in(self, name: str) -> list[str]:
		return list(self._data.get(name, {}).keys())

	def file(self, name: str) -> dict[str, Any] | None:
		return self._data.get(name)

	def files(self) -> list[str]:
		return list(self._data.keys())

	def __getattr__(self, name: str) -> list[str]:
		if name.startswith("_"):
			raise AttributeError(name)
		if name in self._data:
			return list(self._data[name].keys())
		raise AttributeError(f"no data file named {name!r}")
