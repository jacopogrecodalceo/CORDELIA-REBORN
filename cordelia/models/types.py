from enum import Enum, auto

class QualityStage(Enum):
	"""Two passes: first resolve everything knowable in isolation,
	then resolve cross-instrument references (`same X as Y`) now that
	pass one's results are in the symbol table."""
	PRIMARY = auto()
	REFERENCE = auto()


class Status(Enum):
	"""Node status states."""
	INIT = auto()
	RELEASE = auto()
	PATCHED = auto()
	UNPATCHED = auto()


