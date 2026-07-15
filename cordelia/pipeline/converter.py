from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from fractions import Fraction

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
global_var_template = jinja_env.get_template('global_var_init.j2')
bridge_template = jinja_env.get_template('bridge_init.j2')
instr_template = jinja_env.get_template('instr_init.j2')

FT_ORDER = ['cycle', 'talea', 'color', 'dur', 'dyn', 'env', 'space']

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

class CsoundUnit(ABC):
	"""shared lifecycle contract for anything emitted into the orc queue."""
	TURN_OFF2_mode: int
	TURN_OFF2_release: int

	@abstractmethod
	def init(self): ...

	@abstractmethod
	def release(self): ...


class gkInstr(CsoundUnit):

	TURN_OFF2_mode = 0 		# all instances
	TURN_OFF2_release = 0 	# non release

	def __init__(self, name: str, value: list, instrument: Instrument):
		self.value = value
		self.csound_instr_name = f'{instrument.uid}_{name}'
		self.csound_var_name = f'gk{self.csound_instr_name}'

	def _init_var(self):
		return f'{self.csound_var_name} init 0'

	def _schedule(self):
		return f'schedule "{self.csound_instr_name}", 0, -1'

	def _turnoff(self):
		return turnoff2_line(self.csound_instr_name, self.TURN_OFF2_mode, self.TURN_OFF2_release)

	def init(self):
		orc_lines = [
			csound_comment_line(f'GLOBAL VAR {self.csound_instr_name} INIT'),
			self._init_var(),
			global_var_template.render(vars(self)),
			self._schedule()
		]
		emit_orc_lines(orc_lines)

	def release(self):
		orc_lines = [
			csound_comment_line(f'GLOBAL VAR {self.csound_instr_name} RELEASE'),
			f'turnoff2_i nstrnum({self.csound_instr_name})',
			self._turnoff()
		]
		emit_orc_lines(orc_lines)


class CsInstr_Clear(CsoundUnit):

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


class CsInstr_Bridge(CsoundUnit):

	TURN_OFF2_mode = STRICT_TURN_OFF_mode
	TURN_OFF2_release = STRICT_TURN_OFF_release

	def __init__(self, instrument: Instrument):
		self.instrument = instrument

	def instr_num(self, ch):
		return f'nstrnum("{self.instrument.uid}_bridge")+{ch}/1000'

	def _schedule_instr(self):
		orcs = []
		for ch in range(1, CHANNELs + 1):
			orcs.append(f'schedule {self.instr_num(ch)}, 0, -1, {ch}')
		emit_orc_lines(orcs)

	def _make_modifier_params(self, modifier, index):
		if not modifier.items or len(modifier.ins) == 1:
			return []
		params = []
		for i, (slot, values) in enumerate(zip(modifier.ins[1:], modifier.items)):
			if slot in ('k', 'J'):
				name = f'{modifier.name}_{index}_{i}'
				gkinstr = gkInstr(name, values, self.instrument)
				self.instrument.gkinstrs.append(gkinstr)
				gkinstr.init()
				params.append(gkinstr.csound_var_name)
			elif slot == 'S':
				pass  # TODO: string-rate params not yet handled
		return params

	def _make_modifiers_chain(self):
		if not self.instrument.modifiers:
			return 'amain_out = amain_in'

		chain_lines = []
		modifier_index = 0
		while modifier_index < len(self.instrument.modifiers):
			modifier = self.instrument.modifiers[modifier_index]
			if modifier_index == 0:
				params = self._make_modifier_params(modifier, modifier_index + 1)
				extra = ", " + ", ".join(params) if params else ''
				chain_lines.append(f'amain_out {modifier.csound_name} amain_in{extra}')
			else:
				chain_lines.append(f'amain_out {modifier.csound_name} amain_out')
			modifier_index += 1
		return '\n'.join(chain_lines)

	def _make_instr(self):
		chain = self._make_modifiers_chain()
		orcs = [
			csound_comment_line(f'BRIDGE {self.instrument.name}'),
			bridge_template.render(instrument=self.instrument, chain=chain)
		]
		emit_orc_lines(orcs)

	def _turnoff_instr(self):
		orcs = []
		for ch in range(1, CHANNELs + 1):
			orcs.append(turnoff2_line(self.instr_num(ch), self.TURN_OFF2_mode, self.TURN_OFF2_release))
		emit_orc_lines(orcs)

	def init(self):
		self._make_instr()
		self._schedule_instr()

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

		uid = self.instrument.uid    
		cycles = []

		for cycle in self.instrument.qualities['cycle'].resolved:
			if '/' in cycle:
				cycle = float(Fraction(cycle))
			else:
				cycle = int(cycle)/4
			cycles.append(cycle)

		den = 1
		nums = []
		while True:
			if all((v * den).is_integer() for v in cycles):
				nums = [int(v * den) for v in cycles]
				break
			den += 1

		den *= 4

		cums = [0]
		for val in nums[:-1]:  # Exclude last value
			cums.append(cums[-1] + val)

		ftgen_values = [i for i, count in enumerate(nums) for _ in range(count)]

		orc = f'''
gi{ uid }_ts_idx ftgen { ft_num if ft_num else self.ft_num['cycle'] }, 0, giFTGEN_SIZE, -2, {len(ftgen_values)}, { ', '.join(map(str, ftgen_values)) }

gk{ uid }_ts_dur[] fillarray { ', '.join(map(str, nums)) }
gk{ uid }_ts_start[] fillarray { ', '.join(map(str, cums)) }
gk{ uid }_ts_den init { den }
gk{ uid }_ts_total init { sum(nums) }
		'''
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

	def patch(self, previous: InstrumentRuntime):
		orcs = [csound_comment_line('PATCHED')]

		for quality_name, values in self.instrument.qualities.items():
			values = values.resolved
			prev_values = previous.instrument.qualities[quality_name].resolved
			if prev_values != values :
				if quality_name == 'cycle':
					line = self.format_cycle(previous.ft_num['cycle'])
				else:
					line = (
						f'gi{previous.instrument.uid}_{quality_name} ftgen '
						f'{previous.ft_num[quality_name]}, 0, giFTGEN_SIZE, -2, '
						f'{len(values)}, {", ".join(map(str, values))}'
					)
				orcs.append(line)
				previous.instrument.qualities[quality_name].resolved = values
   
		if previous.instrument.modifiers != self.instrument.modifiers:
			previous.bridge.release()
			self.bridge = CsInstr_Bridge(self.instrument)
			self.bridge.init()
		else:
			self.bridge = previous.bridge

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
		session_poems.remove(uid)
	elif state == 'patched':
		previous = session_poems[uid]
		runtime.patch(previous)
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