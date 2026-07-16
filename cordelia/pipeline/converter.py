from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import itertools
from fractions import Fraction

import abjad

from loguru import logger
from cordelia.models.instrument import Instrument
from cordelia.models.variable import Variable
from cordelia.const import jinja_env, csound_comment_line
from cordelia.registry import pool, orc_queue
from cordelia.const import CLEAR_INSTRUMENT_NUM
from config import CHANNELs

# ---------------------------------------------------------------------------- #
#                                LOAD TEMPLATEs                                #
# ---------------------------------------------------------------------------- #
bridge_template = jinja_env.get_template('bridge_init.j2')
instr_template = jinja_env.get_template('instr_init.j2')

FT_ORDER = ['cycle', 'talea', 'color', 'dur', 'dyn', 'env', 'space']

TARGET_DURATION = abjad.Duration(64, 4)
TARGET_LENGTH = 8192

# exact fractional match, non-release -- shared by CsInstr_Clear and CsInstr_Bridge
STRICT_TURN_OFF_mode = 4
STRICT_TURN_OFF_release = 1


def emit_orc_lines(orcs: list):
	orc_queue.put('score', '\n'.join(orcs))


def turnoff2_line(target: str, mode: int, release: int) -> str:
	return f'turnoff2_i {target}, {mode}, {release}'


# ---------------------------------------------------------------------------- #
#                                 CSOUND UNITs                                 #
# ---------------------------------------------------------------------------- #

class CsoundInstrClass(ABC):
	"""shared lifecycle contract for anything emitted into the orc queue."""
	TURN_OFF2_mode: int
	TURN_OFF2_release: int

	@abstractmethod
	def init(self): ...

	@abstractmethod
	def release(self): ...


class GlobalVarInstr(CsoundInstrClass):

	TURN_OFF2_mode = 0 		# all instances
	TURN_OFF2_release = 0 	# non release

	def __init__(self, instrument: Instrument, name: str, value: list = None):
		self.value = value
		self.csound_instr_name = f'{instrument.name}_{name}'
		self.csound_name = f'gk{self.csound_instr_name}'

	def _schedule(self):
		return f'schedule "{self.csound_instr_name}", 0, -1'

	def _turnoff(self):
		return turnoff2_line(f'"{self.csound_instr_name}"', self.TURN_OFF2_mode, self.TURN_OFF2_release)

	def init(self, value=None):
		if value:
			self.value = value    
		orc_lines = [
			csound_comment_line(f'GLOBAL VAR {self.csound_instr_name} INIT'),
			f'\tinstr {self.csound_instr_name}',
			f'{self.csound_name} = {self.value}',
			'\tendin',
			self._schedule()
		]
		emit_orc_lines(orc_lines)

	def release(self):
		orc_lines = [
			csound_comment_line(f'GLOBAL VAR {self.csound_instr_name} RELEASE'),
			self._turnoff()
		]
		emit_orc_lines(orc_lines)

	def __bool__(self):
		return bool(self.value)

class CsInstr_Clear(CsoundInstrClass):

	TURN_OFF2_mode = STRICT_TURN_OFF_mode
	TURN_OFF2_release = STRICT_TURN_OFF_release

	def __init__(self, instrument: Instrument):
		self.instrument = instrument
		self.nums_allocated = []

	def init(self):
		orcs = []
		for ch in range(1, CHANNELs + 1):
			num = pool.clear_instr.alloc()
			self.nums_allocated.append(num)
			orcs.append(f'schedule {CLEAR_INSTRUMENT_NUM + num*10e-3}, 0, -1, "{self.instrument.name}_{ch}"')
		emit_orc_lines(orcs)

	def release(self):
		orcs = []
		for num in self.nums_allocated:
			orcs.append(turnoff2_line(
				f'{CLEAR_INSTRUMENT_NUM + num*10e-3}', self.TURN_OFF2_mode, self.TURN_OFF2_release
			))
			pool.clear_instr.release(num)
		emit_orc_lines(orcs)


class CsInstr_Bridge(CsoundInstrClass):

	TURN_OFF2_mode = STRICT_TURN_OFF_mode
	TURN_OFF2_release = STRICT_TURN_OFF_release

	def __init__(self, instrument: Instrument):
		self.instrument = instrument
		self.active_gk_instr_names = {}
		self.global_var_instr_names = {}

	def instr_num(self, ch):
		return f'nstrnum("{self.instrument.uid}_bridge")+{ch}/1000'

	def _schedule_instr(self):
		orcs = []
		for ch in range(1, CHANNELs + 1):
			orcs.append(f'schedule {self.instr_num(ch)}, 0, -1, {ch}')
		emit_orc_lines(orcs)

	def _make_modifier_params(self, modifier, index):
		for i, slot in enumerate(modifier.udo.real_ins):
			if slot in ('k', 'J'):
				if modifier.items and i < len(modifier.items):
					value = modifier.items[i]
					name = self.make_gk_mod_name(modifier, index, i)
					global_var_instr = self.global_var_instr_names[name]
					global_var_instr.init(value)
					self.active_gk_instr_names[name] = global_var_instr
			elif slot == 'S':
				pass # TODO : string-rate params not yet handled

	def _make_modifiers_chain(self):
		if not self.instrument.modifiers:
			return 'amain_out = amain_in'

		chain_lines = []
		for index, modifier in enumerate(self.instrument.modifiers):
			init_vars = []
			# make init
			for i, init_value in enumerate(modifier.udo.init_values):
				name = self.make_gk_mod_name(modifier, index, i)
				global_var_instr = GlobalVarInstr(self.instrument, name)
				self.global_var_instr_names[name] = global_var_instr
				chain_lines.append(f'{global_var_instr.csound_name} init {init_value}')
				init_vars.append(global_var_instr.csound_name)

			self._make_modifier_params(modifier, index)

			#extra = ", " + ", ".join(self.instrument.global_var_instr_names) if self.instrument.global_var_instr_names else ''
			extra = ', '.join(gkname for gkname in init_vars)
			chain_lines.append(f'amain_out {modifier.udo.name} {'amain_in' if index == 0 else 'amain_out'}, {extra}')

		return '\n'.join(chain_lines)

	def _make_instr(self):
		chain = self._make_modifiers_chain()
		orcs = [
			csound_comment_line(f'BRIDGE {self.instrument.name}'),
			bridge_template.render(instrument=self.instrument, chain=chain)
		]
		emit_orc_lines(orcs)

	def _turnoff_main_bridge_instr(self):
		orcs = []
		for ch in range(1, CHANNELs + 1):
			orcs.append(turnoff2_line(self.instr_num(ch), self.TURN_OFF2_mode, self.TURN_OFF2_release))
		emit_orc_lines(orcs)

	def _turnoff_instr(self):
		self._turnoff_main_bridge_instr()
   
		for global_var_instr in self.active_gk_instr_names.values():
			global_var_instr.release()
		self.active_gk_instr_names.clear()
	
	def init(self):
		self._make_instr()
		self._schedule_instr()

	def make_gk_mod_name(self, modifier, index, j):
		return f'{modifier.name}_m{index+1}p{j+1}'

	def patch(self, current_runtime: InstrumentRuntime):
		for index, modifier in enumerate(current_runtime.instrument.modifiers):
			for i, slot in enumerate(modifier.udo.real_ins):
				if slot in ('k', 'J'):
					name = self.make_gk_mod_name(modifier, index, i)
					# name was used and active
					if name in self.active_gk_instr_names:
						global_var_instr = self.active_gk_instr_names[name]
						global_var_instr.release()
						if modifier.items and i < len(modifier.items):
							value = modifier.items[i]
							global_var_instr.init(value)
							self.active_gk_instr_names[name] = global_var_instr

					# if name wasnt used, but some items
					elif name not in self.active_gk_instr_names and modifier.items and i < len(modifier.items):
						global_var_instr = GlobalVarInstr(self.instrument, name)	
						self.active_gk_instr_names[name] = global_var_instr
						global_var_instr.init(value)

				elif slot == 'S':
					pass # TODO : string-rate params not yet handled

	def release(self):
		self._turnoff_instr()

# ---------------------------------------------------------------------------- #
#                              INSTRUMENT RUNTIME                              #
# ---------------------------------------------------------------------------- #
# owns everything that only exists while an instrument is actually playing:
# allocated ftables, the clear/bridge units, and the diff against whatever
# was playing before it during a patch.

@dataclass
class InstrumentRuntime:
	instrument: Instrument
	clear: CsInstr_Clear = None
	bridge: CsInstr_Bridge = None
	ft_num: dict = field(default_factory=dict)

	def format_cycle(self, ft_num=None):
		def parse_time_signatures(ts_strings: list[str]) -> list[abjad.TimeSignature]:
			"""Turn shorthand strings ('8', '7/8') into TimeSignature objects, defaulting to /4."""
			return [
				abjad.TimeSignature.from_string(ts if "/" in ts else f"{ts}/4")
				for ts in ts_strings
			]
		def build_segments(
			signatures: list[abjad.TimeSignature], target: abjad.Duration
		) -> tuple[list[abjad.Duration], list[abjad.TimeSignature]]:
			"""Cycle through signatures, accumulating durations until target is reached,
			then append the overshoot as a final partial segment."""
			sig_cycle = itertools.cycle(signatures)
			segments: list[abjad.Duration] = []
			used: list[abjad.TimeSignature] = []
			total = abjad.Duration(0)

			while total < target:
				sig = next(sig_cycle)
				segments.append(sig.duration())
				used.append(sig)
				total += segments[-1]

			segments.append(total - target)
			used.append(next(sig_cycle))

			return segments, used

		def distribute_remainder(values: list[float], target_sum: int) -> list[int]:
			"""Largest remainder method: floor each value, then hand out the
			leftover units to the entries with the biggest fractional part."""
			floors = [int(v) for v in values]
			remainder = target_sum - sum(floors)

			fractional_parts = [v - f for v, f in zip(values, floors)]
			order = sorted(range(len(values)), key=lambda i: fractional_parts[i], reverse=True)

			result = floors.copy()
			for i in order[:remainder]:
				result[i] += 1

			return result

		def make_ts(ts_strings: list[str]) -> list:
			"""Build a GEN -25-style breakpoint list (x0, 0, x1, y, x0, 0, x1, y, ...)
			mapping normalized durations to their time-signature ratio."""
			signatures = parse_time_signatures(ts_strings)
			segments, used_signatures = build_segments(signatures, TARGET_DURATION)

			total_duration = sum(segments)
			scaled = [float(seg) * TARGET_LENGTH / float(total_duration) for seg in segments]
			x_values = distribute_remainder(scaled, TARGET_LENGTH)

			y_values = [
				Fraction(float(sig.duration()) / float(seg)).limit_denominator()
				for sig, seg in zip(used_signatures, segments)
			]

			lines = []
			x_sum = 0
			prev_value = 0
			for x, y in zip(x_values, y_values):
				lines += [prev_value, 0, x + x_sum, str(y)]
				prev_value = x + x_sum + 1
				x_sum += x

			return lines

		uid = self.instrument.uid    
		ts = self.instrument.qualities['cycle'].resolved
		orc = f'gi{uid}_cycle ftgen { ft_num if ft_num else self.ft_num['cycle'] }, 0, giFTGEN_SIZE, -27, { ', '.join(map(str, make_ts(ts))) }'
		return orc

	def init(self):
		orcs = [csound_comment_line('INIT')]
		self.ft_num = {name: pool.ft.alloc() for name in FT_ORDER}
		orc = self.format_cycle()
		orcs.append(orc)
		orc = instr_template.render(instrument=self.instrument, ft_num=self.ft_num)
		orcs.append(orc)
		orc = f'schedule "{self.instrument.uid}", 0, -1'
		orcs.append(orc)
		emit_orc_lines(orcs)

		self.clear = CsInstr_Clear(self.instrument)
		self.clear.init()

		self.bridge = CsInstr_Bridge(self.instrument)
		self.bridge.init()

	def patch(self, current_runtime: InstrumentRuntime):
		orcs = [csound_comment_line('PATCHED')]

		for quality_name, values in self.instrument.qualities.items():
			values = values.resolved
			new_values = current_runtime.instrument.qualities[quality_name].resolved
			if values != new_values :
				if quality_name == 'cycle':
					line = self.format_cycle(current_runtime.ft_num['cycle'])
				else:
					line = (
						f'gi{self.instrument.uid}_{quality_name} ftgen '
						f'{self.ft_num[quality_name]}, 0, giFTGEN_SIZE, -2, '
						f'{len(new_values)}, {", ".join(map(str, new_values))}'
					)
				orcs.append(line)
				self.instrument.qualities[quality_name].resolved = new_values
   
		if current_runtime.instrument.modifiers != self.instrument.modifiers:
			if [mod.name for mod in current_runtime.instrument.modifiers] != [mod.name for mod in self.instrument.modifiers]:
				self.bridge.release()
				self.bridge = CsInstr_Bridge(current_runtime.instrument)
				self.bridge.init()
				self.instrument.modifiers = current_runtime.instrument.modifiers
			elif [mod.items for mod in current_runtime.instrument.modifiers] != [mod.items for mod in self.instrument.modifiers]:
				self.bridge.patch(current_runtime)
				self.instrument.modifiers = current_runtime.instrument.modifiers
		emit_orc_lines(orcs)

	def release(self):
		orcs = [csound_comment_line('RELEASE')]
		for ft_num in self.ft_num.values():
			pool.ft.release(ft_num)
			orcs.append(f'; ft num released {ft_num}')

		orcs.append(f'turnoff2_i "{self.instrument.uid}", 0, 0')
		emit_orc_lines(orcs)

		self.clear.release()
		self.bridge.release()


# ---------------------------------------------------------------------------- #
#                                 STATE DISPATCH                               #
# ---------------------------------------------------------------------------- #

session_poems = {}

def convert_instrument(runtime: InstrumentRuntime):
	state = runtime.instrument.state
	logger.debug(f'{state} {runtime.instrument}')

	uid = runtime.instrument.uid

	if state == 'release':
		session_poems[uid].release()
		del session_poems[uid]
	elif state == 'patched':
		session_poems[uid].patch(runtime)
	elif state == 'init':
		runtime.init()
		session_poems[uid] = runtime
	else:
		logger.debug(f'unpatched {runtime.instrument}')


def offer(poems: list):
	for poem in poems:
		if isinstance(poem, Instrument):
			runtime = InstrumentRuntime(instrument=poem)
			convert_instrument(runtime)

		elif isinstance(poem, Variable):
			pass