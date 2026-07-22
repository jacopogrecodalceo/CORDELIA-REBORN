from types import SimpleNamespace
from pathlib import Path

from cordelia.models.csound import CsoundUdo
from cordelia.models.types import QualityStage, Status
from cordelia.models.nodes import QUALITIEs

from cordelia.registry import orc_queue, tracker
from cordelia.registry import registry_quality
from cordelia.pipeline.analysis.resolve import resolve_expr, resolve_func
from cordelia.registry import data

def emit_instr_name(instrument):
	name = instrument.identity.name
	uid = instrument.identity.uid
	if uid in tracker.instrument:
		return True
	tracker.instrument.add(uid)
	instr_orc = Path(data['instrument'].get(name)).read_text()
	orc_queue.put('instrument', instr_orc)

def emit_modifiers(instrument):
	for modifier in instrument.modifiers:
		udo = tracker.modifier.get(modifier.name)
		if not udo:
			udo = CsoundUdo(modifier.name)
			orc_queue.put('modifier', udo.orc)
			tracker.modifier[modifier.name] = udo

		modifier.udo = udo 

def resolve_qualities(instrument):
	for i, verse in enumerate(instrument.verses):
		instrument.verses[i].items = resolve_expr(verse.items)

def resolve_modifiers(instrument):
	for mod in instrument.modifiers:
		if not mod.items:
			continue
		mod.items = resolve_func(instrument, mod.items)

def resolve_variable(variable):
	variable.value = resolve_func(variable, variable.value)

def deduce_qualities(instrument, stage):
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
	for quality in instrument.verses:
		for _quality_name, plugins in registry_quality.items():
			for _name, module in plugins.items():

				if not module.get('stage') == stage:
					continue

				if stage == QualityStage.REFERENCE and instrument.status == Status.UNPATCHED:
					continue

				if module['match'](quality.items):
					args = SimpleNamespace(instrument=instrument, quality=quality)
					module['main'](args)


DATA_TO_LOAD = {k: v for k, v in data.items() if k in ['env', 'mode', 'scala']}

def emit_others(instrument):
	tokens = []
	for quality in QUALITIEs:
		for occurrence in getattr(instrument, quality):
			for t in occurrence.processed:
				tokens.append(t)
	for token in tokens:
		for quality_name, keyword_path_map in DATA_TO_LOAD.items():
			if token in keyword_path_map:
				is_named_token = any(c.isalpha() for c in token)
				local_tracker = getattr(tracker, quality_name)
				if is_named_token and token not in local_tracker:
					with open(keyword_path_map[token]) as f:
						orc_queue.put(quality_name, f.read())
					local_tracker.add(token)