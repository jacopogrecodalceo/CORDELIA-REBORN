from loguru import logger
from cordelia.models.ast import Instrument, Variable
from cordelia.const import jinja_env, csound_comment_line
from cordelia.runtime import pool, orc_queue, tracker
from cordelia.const import CLEAR_INSTRUMENT_NUM
from config import CHANNELs

# ---------------------------------------------------------------------------- #
#                                LOAD TEMPLATEs                                #
# ---------------------------------------------------------------------------- #
global_var_template = jinja_env.get_template('global_var_init.j2')


def emit_orc_lines(orcs: list):
	orc_queue.put('score', '\n'.join(orcs))

class gkInstr:

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
		return f'turnoff2_i {self.csound_instr_name}, {self.TURN_OFF2_mode}, {self.TURN_OFF2_release}'

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

class InstrClear:
	
	TURN_OFF2_mode = 4 		# only turn off notes with exactly matching (fractional) instrument number, rather than ignoring fractional part
	TURN_OFF2_release = 1 	# non release

	def __init__(self, instrument):
		self.instrument = instrument
		self.nums_allocated = []

	def init(self): 
		orcs = []
		for ch in range(1, CHANNELs+1):
			num = pool.clear_instr.alloc()
			self.nums_allocated.append(num)
			orcs.append(f'schedule {CLEAR_INSTRUMENT_NUM + num*10e-3}, 0, -1, "{self.instrument.name}_{ch}"')
		emit_orc_lines(orcs)

	def release(self):
		orcs = []
		for num in self.nums_allocated:
			orcs.append(f'turnoff2_i {CLEAR_INSTRUMENT_NUM + num*10e-3}, {self.TURN_OFF2_mode}, {self.TURN_OFF2_release}')
			pool.clear_instr.release(num)
		emit_orc_lines(orcs)

class InstrBridge:

	TURN_OFF2_mode = 4 		# only turn off notes with exactly matching (fractional) instrument number, rather than ignoring fractional part
	TURN_OFF2_release = 1 	# non release

	def __init__(self, instrument):
		self.instrument = instrument

	def instr_num(self, ch):
		return f'nstrnum("{self.instrument.uid}_bridge")+{ch}/1000'

	def _schedule_instr(self):
		orcs = []
		for ch in range(1, CHANNELs+1):
			orcs.append(f'schedule {self.instr_num(ch)}, 0, -1, {ch}')
		emit_orc_lines(orcs)

	def _make_modifier_params(self, modifier, index):
		if not modifier.values or len(modifier.ins) == 1:
			return []
		params = []
		for i, (slot, values) in enumerate(zip(modifier.ins[1:], modifier.values)):
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
			if modifier_index == 0:
				modifier = self.instrument.modifiers[modifier_index]
				params = self._make_modifier_params(modifier, modifier_index+1)
				line = f'amain_out {modifier.csound_name} amain_in{", " + ', '.join(params) if params else ''}'
				chain_lines.append(line)
				modifier_index += 1
				continue
			modifier = self.instrument.modifiers[modifier_index]
			line = f'amain_out {modifier.csound_name} amain_out'
			chain_lines.append(line)
			modifier_index += 1
		return '\n'.join(chain_lines)

	def _make_instr(self):
		chain = self._make_modifiers_chain()    
		bridge_template = jinja_env.get_template('bridge_init.j2')
		orcs = [
			csound_comment_line(f'BRIDGE {self.instrument.name}'),
			bridge_template.render(instrument=self.instrument, chain=chain)
		]
		emit_orc_lines(orcs)

	def _turnoff_instr(self):
		orcs = []
		for ch in range(1, CHANNELs+1):
			orcs.append(f'turnoff2_i {self.instr_num(ch)}, {self.TURN_OFF2_mode}, {self.TURN_OFF2_release}')
		emit_orc_lines(orcs)

	def init(self):
		self._make_instr()
		self._schedule_instr()

	def release(self):
		self._turnoff_instr()


def _init_ft(instrument):
	order = ['cycle', 'talea', 'colores', 'dur', 'dyn', 'env', 'space']    
	instrument.ft_num = {name: pool.ft.alloc() for name in order}

def _release_ft(instrument):
	for ft_num in instrument.ft_num.values():
		pool.ft.release(ft_num)

def _init_instr(instrument):
	template = jinja_env.get_template('instr_init.j2')
	orc = template.render(instrument=instrument)
	return orc

def _release_instr(instrument):
	return f'turnoff2_i "{instrument.uid}", 0, 0'

def instr_init(instrument):
	orcs = [csound_comment_line('INIT')]   
	_init_ft(instrument)
 
	orcs.append(_init_instr(instrument))
	emit_orc_lines(orcs)

	instrument.clear = InstrClear(instrument)
	instrument.clear.init()

	instrument.bridge = InstrBridge(instrument)
	instrument.bridge.init()

def instr_patch(instrument):
	orcs = [csound_comment_line('PATCHED')]

	for quality_name, values in instrument.score:
		prev_values = getattr(instrument.is_playing_instr.score, quality_name)
		if prev_values != values:
			string = f'gi{instrument.is_playing_instr.uid}_{quality_name} ftgen {instrument.is_playing_instr.ft_num[quality_name]}, 0, giFTGEN_SIZE, -2, {len(values)}, {", ".join(map(str, values))}'
			orcs.append(string)

	prev_mods = instrument.is_playing_instr.modifiers
	if prev_mods != instrument.modifiers:
		instrument.is_playing_instr.bridge.release()

		instrument.bridge = InstrBridge(instrument)
		instrument.bridge.init()

	emit_orc_lines(orcs)
	del instrument.is_playing_instr

def instr_release(instrument):
	orcs = [csound_comment_line('RELEASE')]   
	_release_ft(instrument)
 
	orcs.append(_release_instr(instrument))
	emit_orc_lines(orcs)

	instrument.clear.release()
	instrument.bridge.release()


def convert_instrument(instrument: Instrument):
	if instrument.state == 'release':
		logger.debug(f'release {instrument}')
		instr_release(instrument)
	elif instrument.state == 'patched':
		logger.debug(f'patched {instrument}')
		instr_patch(instrument)
	elif instrument.state == 'init':
		logger.debug(f'init {instrument}')
		instr_init(instrument)
	else:
		logger.debug(f'unpatched {instrument}')

def convert(units: list):
	for unit in units:
		if isinstance(unit, Instrument):
			convert_instrument(unit)
		elif isinstance(unit, Variable):
			pass