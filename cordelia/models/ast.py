from typing import Any, Optional
from dataclasses import dataclass, field

from cordelia.models.score import Score

@dataclass
class Func:
	name: str
	args: list[Any] = field(default_factory=list)

@dataclass
class Array:
	items: list[Any] = field(default_factory=list)

@dataclass
class Quality:
	items: list[Any] = field(default_factory=list)
 
@dataclass
class Modifier:
	kind: str        # "dot" | "colon"
	name: str
	values: Array | None = None
 
	csound_name: Optional[str] = None
	ins: Optional[str] = None
	outs: Optional[str] = None

@dataclass
class PreScore:
	items: list[Quality] = field(default_factory=list)

@dataclass
class Variable:
	name: str
	value: list[Any] = field(default_factory=list)

@dataclass
class Instrument:
	name: str
	modifiers: list[Modifier]
	qualities: list[Quality]

	name_id: int = field(default_factory=1)
	score: Score = field(default_factory=Score)
