from dataclasses import dataclass, field
from typing import Any

@dataclass
class Variable:
	name: str
	items: list[Any] = field(default_factory=list)

