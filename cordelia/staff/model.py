# cordelia/staff.py
from __future__ import annotations
from typing import ClassVar
from pydantic import BaseModel, Field, computed_field, model_validator
from loguru import logger
from cordelia.staff.const import QUALITIEs

class Staff(BaseModel):
	model_config = {'arbitrary_types_allowed': True}

	_ftgen_counter: ClassVar[int] = 1001

	# ── core inputs ──────────────────────────────────────────────
	instrument: str
	talea_raw: list[int]               # raw binary pulse pattern
	colores: list
	staff_dur: float

	# ── optional — derived in validator if empty ──────────────────
	dur: list[float] = Field(default_factory=list)
	dyn: list[float] = Field(default_factory=list)
	env: list[str]   = Field(default_factory=list)
	space: list[int] = Field(default_factory=list)

	# ── ftgen table numbers — assigned in validator ───────────────
	talea_ft_num: int   = 0
	colores_ft_num: int = 0
	dur_ft_num: int     = 0
	dyn_ft_num: int     = 0
	env_ft_num: int     = 0
	space_ft_num: int   = 0

	# ── lifecycle ─────────────────────────────────────────────────
	dirty: bool   = False
	born: bool    = True
	channel: int  = 0

	# ── computed ──────────────────────────────────────────────────
	@computed_field
	@property
	def instr_id(self) -> str:
		return f'i{id(self)}'

	@computed_field
	@property
	def talea(self) -> list[int]:
		result = []
		count = 1
		for x in self.talea_raw:
			if x == 1:
				result.append(count)
				count += 1
			else:
				result.append(0)
		return result

	# ── validation ────────────────────────────────────────────────
	@model_validator(mode='after')
	def _fill_defaults_and_ft_nums(self) -> Staff:
		if not self.dur:
			result, count = [], 1
			for x in reversed(self.talea):
				if x == 0:
					count += 1
				else:
					result.append(count)
					count = 1
			self.dur = list(reversed(result))

		if not self.dyn:
			self.dyn = [1.0] + [0.5] * (len(self.dur) - 1)

		if not self.env:
			self.env = ['gieclassic', 'gieclassic']

		if not self.space:
			self.space = [0]

		for p in QUALITIEs:
			setattr(self, f'{p}_ft_num', Staff._ftgen_counter)
			Staff._ftgen_counter += 1

		logger.debug(f'staff initialized | instrument={self.instrument} | id={self.instr_id}')
		return self

	# ── mutation ──────────────────────────────────────────────────
	def update(self, **kwargs) -> None:
		for key, value in kwargs.items():
			if hasattr(self, key):
				old = getattr(self, key)
				setattr(self, key, value)
				self.dirty = True
				logger.debug(f'staff updated | id={self.instr_id} | {key}: {old!r} → {value!r}')
			else:
				logger.warning(f'staff update ignored | unknown param: {key}')