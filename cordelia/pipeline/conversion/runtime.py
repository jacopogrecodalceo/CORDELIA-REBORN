from __future__ import annotations
from dataclasses import dataclass, field

from cordelia.models.nodes import Instrument, QUALITIEs, Variable
from cordelia.const import csound_comment_line, jinja_env
from cordelia.registry import pool
from cordelia.models.csound import CsInstr_Clear, CsInstr_Bridge, emit_orc_lines

FT_ORDER = ['cycle', 'talea', 'color', 'dur', 'dyn', 'env', 'space']

instr_template = jinja_env.get_template('instr_init.j2')

@dataclass
class SharedRuntime:
	node: Instrument | Variable
	
	@property
	def instrument(self) -> Instrument:
		"""Get node as Instrument (raises TypeError if it's a Variable)."""
		if isinstance(self.node, Instrument):
				return self.node
		raise TypeError(f"Expected Instrument, got Variable")
	
	@property
	def variable(self) -> Variable:
		"""Get node as Variable (raises TypeError if it's an Instrument)."""
		if isinstance(self.node, Variable):
				return self.node
		raise TypeError(f"Expected Variable, got Instrument")

@dataclass
class InstrumentRuntime(SharedRuntime):
	"""Owns everything that only exists while an instrument is actually playing."""
	
	clear: CsInstr_Clear | None = None
	bridge: CsInstr_Bridge | None = None
	ft_num: dict[str, int] = field(default_factory=dict)

	def cycle_template(self):
		return f'gi{self.instrument.identity.uid}_cycle ftgen {self.ft_num['cycle']}, 0, giFTGEN_SIZE, -27, {self.instrument.cycle.ftgen_format(self.instrument)}'

	def talea_template(self):
		lines = [
			f'gk{self.instrument.identity.uid}_talea_num init {len(self.instrument.talea)}',
			f'gi{self.instrument.identity.uid}_talea ftgen {self.ft_num['talea']}, 0, giFTGEN_SIZE, -17, {self.instrument.talea.ftgen_format()}'
		]
		return '\n'.join(lines)

	def init(self) -> None:

		orcs = [csound_comment_line('INIT')]
		self.ft_num = {name: pool.ft.alloc() for name in FT_ORDER}

		orcs.append(self.cycle_template())
		orcs.append(self.talea_template())
		orcs.append(instr_template.render(instrument=self.instrument, ft_num=self.ft_num))
		orcs.append(f'schedule "{self.instrument.identity.uid}", 0, -1')
		emit_orc_lines(orcs)

		self.clear = CsInstr_Clear(self.instrument)
		self.clear.init()

		self.bridge = CsInstr_Bridge(self.instrument)
		self.bridge.init()

	def _patch_qualities(self, current_runtime: InstrumentRuntime) -> list[str]:
		orcs = []
		for quality in QUALITIEs:
			values = getattr(self.instrument, quality).values
			new_values = getattr(current_runtime.instrument, quality).values
			if values == new_values and not getattr(self.instrument, quality).dirty:
				continue

			setattr(self.instrument, quality, getattr(current_runtime.instrument, quality))
			if quality == 'cycle':
				line = self.cycle_template()
			elif quality == 'talea':
				line = self.talea_template()
			else:
				line = (
					f'gi{self.instrument.identity.uid}_{quality} ftgen '
					f'{self.ft_num[quality]}, 0, giFTGEN_SIZE, -2, '
					f'{len(new_values)}, {getattr(self.instrument, quality).ftgen_format()}'
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

		orcs.append(f'turnoff2_i "{self.instrument.identity.uid}", 0, 0')
		emit_orc_lines(orcs)

		self.clear.release()
		self.bridge.release()

class VariableRuntime(SharedRuntime):
	"""Owns everything that only exists while a variable is active."""
	
	def __init__(self, variable: Variable):
		super().__init__(node=variable)
		self.csound_instr_name = f'{variable.identity.name}'
		self.csound_gkvar = f'gk{variable.identity.name}'
	
	def _schedule(self) -> str:
		return f'schedule "{self.csound_instr_name}", 0, -1'
	
	def _turnoff(self) -> str:
		return f'turnoff2_i "{self.csound_instr_name}", 0, 0'
	
	def init(self) -> None:
		orc_lines = [
				csound_comment_line(f'GLOBAL VAR {self.csound_instr_name} INIT'),
				f'\tinstr {self.csound_instr_name}',
				f'{self.csound_gkvar} = {''.join(self.variable.value)}',
				'\tendin',
				self._schedule(),
		]
		emit_orc_lines(orc_lines)
	
	def patch(self, current_variable: VariableRuntime) -> None:
		if self.variable.value != current_variable.variable.value:
				self.release()
				self.variable.value = current_variable.variable.value
				self.init()
	
	def release(self) -> None:
		orc_lines = [
				csound_comment_line(f'GLOBAL VAR {self.csound_instr_name} RELEASE'),
				self._turnoff(),
		]
		emit_orc_lines(orc_lines)