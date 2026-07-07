from loguru import logger
from cordelia.models.ast import Instrument, Variable
from cordelia.const import jinja_env, csound_comment_line
from cordelia.runtime import pool, orc_queue, tracker
from cordelia.const import CLEAR_INSTRUMENT_NUM
from config import CHANNELs

def emit_orcs(orcs: list):
	orc_queue.put('score', '\n'.join(orcs))

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
		emit_orcs(orcs)

	def release(self):
		orcs = []
		for num in self.nums_allocated:
			orcs.append(f'turnoff2_i {CLEAR_INSTRUMENT_NUM + num*10e-3}, {self.TURN_OFF2_mode}, {self.TURN_OFF2_release}')
			pool.clear_instr.release(num)
		emit_orcs(orcs)

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
		emit_orcs(orcs)

	def _make_modifiers_chain(self):
		if not self.instrument.modifiers:
			return 'amain_out = amain_in'

	def _make_instr(self):
		chain = self._make_modifiers_chain()    
		bridge_template = jinja_env.get_template('bridge_init.j2')
		orcs = [
			csound_comment_line(f'BRIDGE {self.instrument.name}'),
			bridge_template.render(instrument=self.instrument, chain=chain)
		]
		emit_orcs(orcs)

	def _turnoff_instr(self):
		orcs = []
		for ch in range(1, CHANNELs+1):
			orcs.append(f'turnoff2_i {self.instr_num(ch)}, {self.TURN_OFF2_mode}, {self.TURN_OFF2_release}')
		emit_orcs(orcs)

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
	emit_orcs(orcs)

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
	emit_orcs(orcs)
	del instrument.is_playing_instr

def instr_release(instrument):
	orcs = [csound_comment_line('RELEASE')]   
	_release_ft(instrument)
 
	orcs.append(_release_instr(instrument))
	emit_orcs(orcs)

	instrument.clear.release()
	instrument.bridge.release()


def convert_instrument(instrument: Instrument):
	if instrument.state == 'release':
		instr_release(instrument)
	elif instrument.state == 'patched':
		instr_patch(instrument)
	elif instrument.state == 'init':
		instr_init(instrument)

def convert(units: list):
	for unit in units:
		if isinstance(unit, Instrument):
			convert_instrument(unit)
		elif isinstance(unit, Variable):
			pass