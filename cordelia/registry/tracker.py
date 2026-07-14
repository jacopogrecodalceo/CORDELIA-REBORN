from dataclasses import dataclass, field

@dataclass
class Tracker:
	instrument: set = field(default_factory=set)
	modifier: dict = field(default_factory=dict)
	env: set = field(default_factory=set)
	mode: set = field(default_factory=set)
	scala: set = field(default_factory=set)
	uid: dict = field(default_factory=dict)

tracker = Tracker()