from dataclasses import dataclass, field
import re
from pathlib import Path
from types import SimpleNamespace

from cordelia.models.instrument import Instrument
from cordelia.models.variable import Variable

from cordelia.pipeline.transformer import Expr, Repeat

from cordelia.registry import registry_quality, registry_func
from cordelia.registry import data
from cordelia.registry import orc_queue, tracker
from cordelia.errors import *


OPCODE_RE = re.compile(
	r"opcode\s+(cordelia_\w+)\s*,\s*([^,]+)\s*,\s*([^\n\r]+)",
	re.MULTILINE
)

CORDELIA_INIT_RE = re.compile(
	r';\s*CORDELIA INIT:\s*(.+)'
)


@dataclass
class CsUDO:
	name: str
	ins: str
	outs: str
	raw_init_values: list
	real_ins: str = field(default_factory=str)
	init_values: list = field(default_factory=list)

	def __post_init__(self):
		self.real_ins = self.ins[1:]
		assert self.ins[0] == 'a', f'NO a in OPCODE {self.name}'

		values = []
		# anal init values:
		for v in self.raw_init_values:
			match = re.search(r'p(\d+)=(.*)', v)
			if match:
				num = match.group(1)
				value = match.group(2)
				values.append((num, value))
			else:
				assert int(v), f'{self.name} {v} is not an int'
				values.append(v)

		
		assert len(self.real_ins) == len(values)
		for i, v in enumerate(values):
			if len(v) > 1:
				num, value = v
				assert i+1 == int(num)
				self.init_values.append(value)
			else:
				self.init_values.append(v)
				

def _deduce_name(instrument):
	instrument.uid = f'{instrument.name}_{instrument.cordelia_id}'
	if instrument.name in tracker.instrument:
		return True
	path = Path(data['instrument'].get(instrument.name))
	tracker.instrument.add(instrument.name)
	orc_queue.put('instrument', path.read_text())

def _deduce_modifiers(instrument):
	def parse_udo(source):
		matches = list(OPCODE_RE.finditer(source))
		assert len(matches) == 1, f"MORE THAN ONE cordelia_ opcode recognised in the file {matches}"
		csound_name, outs, ins = matches[0].groups()
		return csound_name, ins, outs

	def parse_cordelia_init(line):
		match = re.search(CORDELIA_INIT_RE, line)
		if not match:
			return None
		return [p.strip() for p in match.group(1).split(',')]

	for modifier in instrument.modifiers:
		udo = tracker.modifier.get(modifier.name)
		if not udo:
			path = Path(data['modifier'].get(modifier.name))
			modifier_orc = path.read_text()
			csound_name, ins, outs = parse_udo(modifier_orc)
			init_values = parse_cordelia_init(modifier_orc)
			udo = CsUDO(csound_name, ins, outs, init_values)
			orc_queue.put('modifier', modifier_orc)
			tracker.modifier[modifier.name] = udo

		modifier.udo = udo

def parse_quality(items: list):
	parsed_items = []
	for item in items:
		if isinstance(item, Expr):
			parsed_items.extend(item.items)
		elif isinstance(item, Repeat):
			parsed_items.extend(item)
		else:
			parsed_items.append(item)
	return parsed_items   

def _deduce_qualities(instrument):
	"""
	registry_quality[name] = {
		'main': function main,
		'match': function main match,
	}

	i.e.
	registry_quality[talea] = {
		'eu': {
			'main': function main,
			'match': function main match,
		}
	}
	"""
	for quality in instrument.qualities_raw:
		matched = False
		for _quality_name, plugins in registry_quality.items():
			for _name, module in plugins.items():
				quality.items = parse_quality(quality.items)
				if module['match'](quality.items):
					args = SimpleNamespace(instrument=instrument, quality=quality)
					module['main'](args)
					matched = True
		if not matched:
			raise CordeliaDeductionError(f"no plugin matched quality: {quality.items}")

def deduce_function(instrument, func):
	fn = registry_func.get(func.name, None)
	if fn:
		args = SimpleNamespace(instrument=instrument, values=func.args)
		fn(args)
		return True
	raise CordeliaDeductionError(f"no plugin matched func: {func.name}")

def deduce(poem):
	if isinstance(poem, Instrument):
		instrument = poem
		_deduce_name(instrument)
		_deduce_modifiers(poem)
		_deduce_qualities(poem)
	elif isinstance(poem, Variable):
		pass

