from email.policy import default
import re
from dataclasses import dataclass, field
from typing import Any, Union, Optional, Type
from cordelia.pipeline.deduction import Quality
from cordelia.pipeline.quality_models import *

@dataclass
class Func:
	name: str
	args: list[Any] = field(default_factory=list)


@dataclass
class Array:
	items: list[Any] = field(default_factory=list)


@dataclass
class Mod:
	kind: str        # "dot" | "colon"
	name: str
	array: Array | None = None


@dataclass
class Score:
   qualities: list[Quality] = field(default_factory=list)

   def __post_init__(self):
      for quality in self.qualities:
         quality.items = self._expand(quality.items)

   @classmethod


QUALITY_CLASSEs = [Talea, Colores, Dur, Dyn, Env, Space]
QualityType = Union[Talea, Colores, Dur, Dyn, Env, Space]

@dataclass
class Instrument:
	name: str
	qualities: list[QualityType] = field(default_factory=list)
	modifiers: list[Mod] = field(default_factory=list)
	auto_fill: bool = True

	def __post_init__(self):
		if self.auto_fill:
			self.fill_missing_qualities()

	def fill_missing_qualities(self) -> None:
		"""Add default instances for missing quality classes."""
		existing_types = {type(q).__name__ for q in self.qualities}
		
		for quality_class in QUALITY_CLASSEs:
			class_name = quality_class.__name__
			if class_name not in existing_types:
					self.qualities.append(quality_class())
					print(f"✅ Added default {class_name} to {self.name}")

	def get_quality(self, quality_type: Type) -> Optional[QualityType]:
		"""Get a specific quality by type."""
		for q in self.qualities:
			if isinstance(q, quality_type):
					return q
		return None

	def has_all_qualities(self) -> bool:
		"""Check if all quality classes are present."""
		existing_types = {type(q).__name__ for q in self.qualities}
		return all(cls.__name__ in existing_types for cls in QUALITY_CLASSEs)



@dataclass
class Variable:
	name: str
	value: list[Any] = field(default_factory=list)
