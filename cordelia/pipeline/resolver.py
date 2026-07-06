from cordelia.models.ast import Instrument, Variable, Modifier
from cordelia.runtime import tracker, orc_queue
from cordelia.const import data
from cordelia.pipeline.deducer import deduce_quality

class CordeliaResolveError(Exception):
	pass

import re

OPCODE_RE = re.compile(
	r"opcode\s+(cordelia_\w+)\s*,\s*([^,]+)\s*,\s*([^\n\r]+)",
	re.MULTILINE
)

def parse_modifier(source):
	opcode = []
	for match in OPCODE_RE.finditer(source):
		csound_name, outs, ins = match.groups()

		opcode.append((csound_name, ins, outs))
	assert len(opcode) == 1, f"MORE THAN ONE cordelia_ opcode recognised in the file {opcode}"

	return opcode[0]

def _resolve_instrument_name(name: str) -> bool:
	if name in tracker.instrument:
		return True
	orc = data['instrument'].get(name)
	if not orc:
		raise CordeliaResolveError(f"Cannot resolve '{name}'")
	tracker.instrument.add(name)
	with open(orc, 'r') as f:
		orc_queue.instrument.add(f.read())
	return True


def _resolve_modifier(modifier: Modifier) -> bool:
	name = modifier.name
	already_resolved = tracker.modifier.get(name, False)
	if not already_resolved:
		modifier_path = data['modifier'].get(name)
		with open(modifier_path, 'r') as f:
			modifier_orc = f.read()
		csound_name, ins, outs = parse_modifier(modifier_orc)
		orc_queue.modifier.add(modifier_orc)
		tracker.modifier[name] = (csound_name, ins, outs)
	else:
		csound_name, ins, outs = already_resolved
	modifier.csound_name = csound_name
	modifier.ins = ins
	modifier.outs = outs
	return True

def resolve(unit: Instrument | Variable):
	if isinstance(unit, Instrument):
		errors = []

		try:
			_resolve_instrument_name(unit.name)
		except CordeliaResolveError as e:
			errors.append(e)

		for modifier in unit.modifiers:
			try:
				_resolve_modifier(modifier)
			except CordeliaResolveError as e:
				errors.append(e)

		if errors:
			raise ExceptionGroup("failed to resolve", errors)

		for quality in unit.qualities:
			deduce_quality(quality, unit)
	elif isinstance(unit, Variable):
		pass