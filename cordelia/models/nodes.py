from __future__ import annotations

from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from cordelia.models.ast import *
from cordelia.models.types import *
from cordelia.models.qualities import *

from cordelia.errors import CordeliaValidationError
from cordelia.registry import data

@dataclass(slots=True)
class Identity:
	"""Identity with automatic UID generation."""

	name: str
	voice_id: int = 1
	uid: str = field(init=False)

	def __post_init__(self) -> None:
		self.make()

	def make(self) -> None:
		"""Validate and generate UID."""
		if not self.name:
			raise CordeliaValidationError("identity requires a name")
		if self.voice_id < 1:
			raise CordeliaValidationError(f"voice_id must be >= 1, got {self.voice_id}")
		self.uid = f"{self.name}_{self.voice_id}"

@dataclass(slots=True)
class Modifier:
	"""Quality modifier definition."""
	kind: str
	name: str
	items: list = field(default_factory=list)
	udo: object = field(default_factory=object, init=False)




@dataclass(slots=True)
class Node(ABC):
	"""Abstract base for all AST nodes."""
	identity: Identity
	status: Status | None = field(init=False, default=None)
	prev_state: Status | None = field(init=False, default=None)

	@abstractmethod
	def validate(self) -> None:
		"""Check internal consistency (e.g., required fields, types)."""
		...

@dataclass(slots=True)
class Variable(Node):
	value: list

	def validate(self):
		if not self.value:
			raise ValueError(f"Variable '{self.identity.name}' has empty value")



QUALITIEs = {'cycle', 'talea', 'color', 'dur', 'dyn', 'env', 'space'}

@dataclass(slots=True)
class Instrument(Node):
	modifiers: list[Modifier] = field(default_factory=list)
	verses: list[Verse] = field(default_factory=list)

	cycle: Cycle = field(default_factory=Cycle)
	talea: Talea = field(default_factory=Talea)
	color: Color = field(default_factory=Color)
	dur: Dur = field(default_factory=Dur)
	dyn: Dyn = field(default_factory=Dyn)
	env: Env = field(default_factory=Env)
	space: Space = field(default_factory=Space)

	def validate(self):
		if self.identity.name not in data['instrument']:
			raise CordeliaValidationError(f"cannot find '{self.identity.name}' in instrument json · probably a typing error?")
		for modifier in self.modifiers:
			if modifier.name not in data['modifier']:
				raise CordeliaValidationError(f"cannot find '{modifier.name}' in modifier json · probably a typing error?")
