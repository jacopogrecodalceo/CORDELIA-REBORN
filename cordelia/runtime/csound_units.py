from __future__ import annotations

from abc import ABC, abstractmethod

from cordelia.models.instrument import Instrument
from cordelia.const import csound_comment_line
from cordelia.registry import pool, orc_queue
from cordelia.const import CLEAR_INSTRUMENT_NUM
from config import CHANNELs

# exact fractional match, non-release -- shared by CsInstr_Clear and CsInstr_Bridge
STRICT_TURN_OFF_mode = 4
STRICT_TURN_OFF_release = 1


def emit_orc_lines(orcs: list) -> None:
	orc_queue.put('score', '\n'.join(orcs))


def turnoff2_line(target: str, mode: int, release: int) -> str:
	return f'turnoff2_i {target}, {mode}, {release}'


class CsoundInstrClass(ABC):
	"""Shared lifecycle contract for anything emitted into the orc queue."""

	turn_off2_mode: int
	turn_off2_release: int

	def __init_subclass__(cls, **kwargs) -> None:
		super().__init_subclass__(**kwargs)
		for required in ('turn_off2_mode', 'turn_off2_release'):
			if not hasattr(cls, required):
				raise TypeError(f'{cls.__name__} must define {required}')

	@abstractmethod
	def init(self) -> None: ...

	@abstractmethod
	def release(self) -> None: ...


class GlobalVarInstr(CsoundInstrClass):

	turn_off2_mode = 0 		# all instances
	turn_off2_release = 0 	# non release

	def __init__(self, instrument: Instrument, name: str, value: list | None = None):
		self.value = value
		self.csound_instr_name = f'{instrument.name}_{name}'
		self.csound_name = f'gk{self.csound_instr_name}'

	@property
	def has_value(self) -> bool:
		return bool(self.value)

	def _schedule(self) -> str:
		return f'schedule "{self.csound_instr_name}", 0, -1'

	def _turnoff(self) -> str:
		return turnoff2_line(f'"{self.csound_instr_name}"', self.turn_off2_mode, self.turn_off2_release)

	def init(self, value=None) -> None:
		if value:
			self.value = value
		orc_lines = [
			csound_comment_line(f'GLOBAL VAR {self.csound_instr_name} INIT'),
			f'\tinstr {self.csound_instr_name}',
			f'{self.csound_name} = {self.value}',
			'\tendin',
			self._schedule(),
		]
		emit_orc_lines(orc_lines)

	def release(self) -> None:
		orc_lines = [
			csound_comment_line(f'GLOBAL VAR {self.csound_instr_name} RELEASE'),
			self._turnoff(),
		]
		emit_orc_lines(orc_lines)


class CsInstr_Clear(CsoundInstrClass):

	turn_off2_mode = STRICT_TURN_OFF_mode
	turn_off2_release = STRICT_TURN_OFF_release

	def __init__(self, instrument: Instrument):
		self.instrument = instrument
		self.nums_allocated: list[int] = []

	def init(self) -> None:
		orcs = []
		for ch in range(1, CHANNELs + 1):
			num = pool.clear_instr.alloc()
			self.nums_allocated.append(num)
			orcs.append(f'schedule {CLEAR_INSTRUMENT_NUM + num*10e-3}, 0, -1, "{self.instrument.name}_{ch}"')
		emit_orc_lines(orcs)

	def release(self) -> None:
		orcs = []
		for num in self.nums_allocated:
			orcs.append(turnoff2_line(
				f'{CLEAR_INSTRUMENT_NUM + num*10e-3}', self.turn_off2_mode, self.turn_off2_release
			))
			pool.clear_instr.release(num)
		emit_orc_lines(orcs)


class CsInstr_Bridge(CsoundInstrClass):

	turn_off2_mode = STRICT_TURN_OFF_mode
	turn_off2_release = STRICT_TURN_OFF_release

	def __init__(self, instrument: Instrument):
		self.instrument = instrument
		self.active_gk_instr_names: dict[str, GlobalVarInstr] = {}
		self.global_var_instr_names: dict[str, GlobalVarInstr] = {}

	def instr_num(self, ch: int) -> str:
		return f'nstrnum("{self.instrument.uid}_bridge")+{ch}/1000'

	def make_gk_mod_name(self, modifier, index: int, j: int) -> str:
		return f'{modifier.name}_m{index+1}p{j+1}'

	def _schedule_instr(self) -> None:
		orcs = [
			f'schedule {self.instr_num(ch)}, 0, -1, {ch}'
			for ch in range(1, CHANNELs + 1)
		]
		emit_orc_lines(orcs)

	def _make_modifier_params(self, modifier, index: int) -> None:
		for i, slot in enumerate(modifier.udo.real_ins):
			if slot in ('k', 'J'):
				if modifier.items and i < len(modifier.items):
					value = modifier.items[i]
					name = self.make_gk_mod_name(modifier, index, i)
					global_var_instr = self.global_var_instr_names[name]
					global_var_instr.init(value)
					self.active_gk_instr_names[name] = global_var_instr
			elif slot == 'S':
				pass  # TODO: string-rate params not yet handled

	def _make_modifiers_chain(self):
		if not self.instrument.modifiers:
			return 'amain_out = amain_in'

		chain_lines = []
		for index, modifier in enumerate(self.instrument.modifiers):
			init_vars = []
			# make init
			for i, (kind, init_value) in enumerate(modifier.udo.init_values):
				if kind == 'k':
					name = self.make_gk_mod_name(modifier, index, i)
					global_var_instr = GlobalVarInstr(self.instrument, name)
					self.global_var_instr_names[name] = global_var_instr
					chain_lines.append(f'{global_var_instr.csound_name} init {init_value}')
				init_vars.append((kind, init_value, global_var_instr.csound_name))

			self._make_modifier_params(modifier, index)

			#extra = ", " + ", ".join(self.instrument.global_var_instr_names) if self.instrument.global_var_instr_names else ''
			extra = []
			for kind, init_value, gkname in init_vars:
				if kind == 'k':
					extra.append(gkname)
				elif kind == 'i':
					extra.append(init_value)
   
			chain_lines.append(f'amain_out {modifier.udo.name} {'amain_in' if index == 0 else 'amain_out'}, {', '.join(extra)}')

		return '\n'.join(chain_lines)


	def _make_instr(self) -> None:
		from cordelia.const import jinja_env
		bridge_template = jinja_env.get_template('bridge_init.j2')
		chain = self._make_modifiers_chain()
		orcs = [
			csound_comment_line(f'BRIDGE {self.instrument.name}'),
			bridge_template.render(instrument=self.instrument, chain=chain),
		]
		emit_orc_lines(orcs)

	def _turnoff_main_bridge_instr(self) -> None:
		orcs = [
			turnoff2_line(self.instr_num(ch), self.turn_off2_mode, self.turn_off2_release)
			for ch in range(1, CHANNELs + 1)
		]
		emit_orc_lines(orcs)

	def _turnoff_instr(self) -> None:
		self._turnoff_main_bridge_instr()
		for global_var_instr in self.active_gk_instr_names.values():
			global_var_instr.release()
		self.active_gk_instr_names.clear()

	def init(self) -> None:
		self._make_instr()
		self._schedule_instr()

	def patch(self, current_runtime) -> None:
		for index_mod, modifier in enumerate(current_runtime.instrument.modifiers):
			for index_slot, slot in enumerate(modifier.udo.real_ins):
				if slot in ('k', 'J'):
					name = self.make_gk_mod_name(modifier, index_mod, index_slot)
					# name was used and active
					if name in self.active_gk_instr_names:
						global_var_instr = self.active_gk_instr_names[name]
						if modifier.items and index_slot < len(modifier.items):
							new_value = modifier.items[index_slot]
							value = self.instrument.modifiers[index_mod].items[index_slot]
							if new_value != value:
								global_var_instr.release()
								global_var_instr.init(new_value)
								self.active_gk_instr_names[name] = global_var_instr

					# if name wasnt used, but some items
					elif name not in self.active_gk_instr_names and modifier.items and index_slot < len(modifier.items):
						value = modifier.items[index_slot]
						global_var_instr = GlobalVarInstr(self.instrument, name)	
						self.active_gk_instr_names[name] = global_var_instr
						global_var_instr.init(value)

				elif slot == 'S':
					pass # TODO : string-rate params not yet handled

	def release(self) -> None:
		self._turnoff_instr()