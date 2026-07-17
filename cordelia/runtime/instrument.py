from __future__ import annotations

from dataclasses import dataclass, field

from cordelia.models.instrument import Instrument
from cordelia.const import csound_comment_line, jinja_env
from cordelia.registry import pool
from cordelia.runtime.csound_units import CsInstr_Clear, CsInstr_Bridge, emit_orc_lines
from cordelia.runtime.cycle_format import format_cycle_ftgen

FT_ORDER = ['cycle', 'talea', 'color', 'dur', 'dyn', 'env', 'space']

instr_template = jinja_env.get_template('instr_init.j2')


@dataclass
class InstrumentRuntime:
	"""Owns everything that only exists while an instrument is actually playing:
	allocated ftables, the clear/bridge units, and the diff against whatever
	was playing before it during a patch."""

	instrument: Instrument
	clear: CsInstr_Clear | None = None
	bridge: CsInstr_Bridge | None = None
	ft_num: dict[str, int] = field(default_factory=dict)

	def _cycle_ftgen_line(self, ft_num: int | None = None) -> str:
		ts = self.instrument.qualities['cycle'].resolved
		return format_cycle_ftgen(
			uid=self.instrument.uid,
			ts_strings=ts,
			ft_num=ft_num if ft_num else self.ft_num['cycle'],
		)

	def init(self) -> None:
		orcs = [csound_comment_line('INIT')]
		self.ft_num = {name: pool.ft.alloc() for name in FT_ORDER}

		orcs.append(self._cycle_ftgen_line())
		orcs.append(instr_template.render(instrument=self.instrument, ft_num=self.ft_num))
		orcs.append(f'schedule "{self.instrument.uid}", 0, -1')
		emit_orc_lines(orcs)

		self.clear = CsInstr_Clear(self.instrument)
		self.clear.init()

		self.bridge = CsInstr_Bridge(self.instrument)
		self.bridge.init()

	def _patch_qualities(self, current_runtime: InstrumentRuntime) -> list[str]:
		orcs = []
		for quality_name, values in self.instrument.qualities.items():
			values = values.resolved
			new_values = current_runtime.instrument.qualities[quality_name].resolved
			if values == new_values and not self.instrument.qualities[quality_name].dirty:
				continue

			self.instrument.qualities[quality_name].resolved = new_values

			if quality_name == 'cycle':
				line = self._cycle_ftgen_line(self.ft_num['cycle'])
			else:
				line = (
					f'gi{self.instrument.uid}_{quality_name} ftgen '
					f'{self.ft_num[quality_name]}, 0, giFTGEN_SIZE, -2, '
					f'{len(new_values)}, {", ".join(map(str, new_values))}'
				)
			orcs.append(line)
		return orcs

	def _patch_modifiers(self, current_runtime: InstrumentRuntime) -> None:
		if current_runtime.instrument.modifiers == self.instrument.modifiers:
			return

		current_names = [mod.name for mod in current_runtime.instrument.modifiers]
		self_names = [mod.name for mod in self.instrument.modifiers]

		if current_names != self_names:
			self.bridge.release()
			self.bridge = CsInstr_Bridge(current_runtime.instrument)
			self.bridge.init()
			self.instrument.modifiers = current_runtime.instrument.modifiers
			return

		current_items = [mod.items for mod in current_runtime.instrument.modifiers]
		self_items = [mod.items for mod in self.instrument.modifiers]
		if current_items != self_items:
			self.bridge.patch(current_runtime)
			self.instrument.modifiers = current_runtime.instrument.modifiers

	def patch(self, current_runtime: InstrumentRuntime) -> None:
		orcs = [csound_comment_line('PATCHED')]
		orcs.extend(self._patch_qualities(current_runtime))
		self._patch_modifiers(current_runtime)
		emit_orc_lines(orcs)

	def release(self) -> None:
		orcs = [csound_comment_line('RELEASE')]
		for ft_num in self.ft_num.values():
			pool.ft.release(ft_num)
			orcs.append(f'; ft num released {ft_num}')

		orcs.append(f'turnoff2_i "{self.instrument.uid}", 0, 0')
		emit_orc_lines(orcs)

		self.clear.release()
		self.bridge.release()