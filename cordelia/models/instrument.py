from dataclasses import dataclass, field
from typing import Any

from cordelia.models.qualities import QUALITIEs
from cordelia.registry import data, orc_queue, tracker

DATA_TO_LOAD = {k: v for k, v in data.items() if k in ['env', 'mode', 'scala']}

@dataclass
class Modifier:
	kind: str
	name: str
	items: list[Any] = field(default_factory=list)

@dataclass
class QualityEntry:
	deduced: Any
	raws: Any

class Quality:
	def __init__(self):
		self.entries: list[QualityEntry] = []
		self.resolved = []

	def add(self, deduced, raws=None):
		self.entries.append(QualityEntry(deduced=deduced, raws=raws))

	def __bool__(self):
		"""Return False if Quality has no entries, True otherwise."""
		return bool(self.entries)

	def __repr__(self):
		if not self.resolved:
			return f'UNRESOLVED: {self.entries!r}'
		else:
			return f'{self.resolved!r}'

@dataclass
class Instrument:
	name: str
	cordelia_id: int
	uid: str = None

	modifiers: list[Modifier] = field(default_factory=list)

	qualities_raw: list = field(default_factory=list)
	qualities: dict = field(
		default_factory=lambda: {name: Quality() for name in QUALITIEs}
	)

	def fill(self):
		for quality_name, quality_obj in self.qualities.items():
			if not quality_obj:
				quality_obj.add(QUALITIEs[quality_name]['default'])
	
	def load(self):
		tokens = [e for token in self.qualities.values() for entry in token.entries for e in entry.deduced]
		for token in tokens:
			for quality_name, keyword_path_map in DATA_TO_LOAD.items():
				if token in keyword_path_map:
					is_named_token = any(c.isalpha() for c in token)
					local_tracker = getattr(tracker, quality_name)
					if is_named_token and token not in local_tracker:
						with open(keyword_path_map[token]) as f:
							orc_queue.put(quality_name, f.read())
						local_tracker.add(token)

	def define(self):
		for quality_name, quality in self.qualities.items():
			fn = QUALITIEs[quality_name]['define']
			quality.resolved = fn(self)
   
	def process(self):
		self.fill()
		self.load()
		self.define()
