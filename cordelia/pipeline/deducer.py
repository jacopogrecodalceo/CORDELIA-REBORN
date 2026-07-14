import re
from pathlib import Path
from types import SimpleNamespace

from cordelia.pipeline.transformer import Instrument, Variable
from cordelia.pipeline.transformer import Expr, Repeat

from cordelia.registry import registry_quality, registry_func
from cordelia.registry import data
from cordelia.registry import orc_queue, tracker
from cordelia.errors import *


OPCODE_RE = re.compile(
	r"opcode\s+(cordelia_\w+)\s*,\s*([^,]+)\s*,\s*([^\n\r]+)",
	re.MULTILINE
)

def _deduce_name(instrument):
	instrument.uid = f'{instrument.name}_{instrument.cordelia_id}'
	if instrument.name in tracker.instrument:
		return True
	path = Path(data['instrument'].get(instrument.name))
	tracker.instrument.add(instrument.name)
	orc_queue.put('instrument', path.read_text())

def _deduce_modifiers(instrument):
	def parse_modifier(source):
		matches = list(OPCODE_RE.finditer(source))
		assert len(matches) == 1, f"MORE THAN ONE cordelia_ opcode recognised in the file {matches}"
		csound_name, outs, ins = matches[0].groups()
		return csound_name, ins, outs

	for modifier in instrument.modifiers:
		cached = tracker.modifier.get(modifier.name)
		if cached is None:
			path = Path(data['modifier'].get(modifier.name))
			modifier_orc = path.read_text()
			cached = parse_modifier(modifier_orc)
			orc_queue.put('modifier', modifier_orc)
			tracker.modifier[modifier.name] = cached
		modifier.csound_name, modifier.ins, modifier.outs = cached

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

