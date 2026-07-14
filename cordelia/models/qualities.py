from cordelia.errors import *
import operator

_OPS = {
	'+': operator.add,
	'-': operator.sub,
	'*': operator.mul,
	'/': operator.truediv,
	'=': None,
}

QUALITIEs = {}

def quality(name, default):
	def register(fn):
		QUALITIEs[name] = {'default': default, 'define': fn}
		return fn
	return register

def sum_entries(entries: list):
	"""[QualityEntry(deduced=[8], raws=[...]), QualityEntry(deduced=[4], raws=[...])]"""
	result = []
	for entry in entries:
		result.extend(entry.deduced)
	return result

# ---------------------------------------------------------------------------- #
#                                   QUALITIEs                                  #
# ---------------------------------------------------------------------------- #


@quality('cycle', default=[8])
def _(instrument):
	return sum_entries(instrument.qualities['cycle'].entries)

@quality('talea', default=[])
def _(instrument):
	count = 1
	result = []
	for entry in sum_entries(instrument.qualities['talea'].entries):
		v = int(entry)
		if v > 0:
			result.append(count)
			count += 1
		else:
			result.append(v)
	return result

@quality('color', default=[1])
def _(instrument):
	return sum_entries(instrument.qualities['color'].entries)

@quality('dur', default=[1])
def _(instrument):
	def make_durs_from_talea(talea: list) -> list:
		durs = []
		count = 1
		for value in reversed(talea):
			if value == 0:
				count += 1
			else:
				durs.append(count)
				count = 1
		durs.reverse()
		durs[-1] += count - 1
		return durs

	deduced_durs = sum_entries(instrument.qualities['dur'].entries)
	talea_durs = make_durs_from_talea(sum_entries(instrument.qualities['talea'].entries))

	if 'dur' not in deduced_durs:
		return talea_durs

	index_dur = deduced_durs.index('dur')
	op_symbol = deduced_durs[index_dur + 1]
	dur_values = deduced_durs[index_dur + 2:]
	if isinstance(dur_values[0], list):
		dur_values = dur_values[0]

	if op_symbol == '=':
		return dur_values
	else:
		op = _OPS[op_symbol]
		return [
			op(float(talea_dur), float(dur_values[i % len(dur_values)]))
			for i, talea_dur in enumerate(talea_durs)
		]

@quality('dyn', default=['mf'])
def _(instrument):
	dyns_macroed = []
	for value in sum_entries(instrument.qualities['dyn'].entries):
		dyns_macroed.append(rf'${value}')
	return dyns_macroed

@quality('env', default=['cls'])
def _(instrument):
	env_gi = []
	for value in sum_entries(instrument.qualities['env'].entries):
		env_gi.append(f'gi{value}')
	return env_gi

@quality('space', default=[0])
def _(instrument):
	return sum_entries(instrument.qualities['space'].entries)

@quality('char', default=[])
def _(instrument):
	return sum_entries(instrument.qualities['char'].entries)