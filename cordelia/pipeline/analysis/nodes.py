from types import SimpleNamespace
from pathlib import Path

from loguru import logger

from cordelia.models.csound import CsoundUdo
from cordelia.models.types import QualityStage, Status
from cordelia.models.nodes import QUALITIEs

from cordelia.const import JINJA_SONVS_TEMPLATE_ENV

from cordelia.registry import orc_queue, tracker
from cordelia.registry import registry_quality
from cordelia.pipeline.analysis.resolve import resolve_expr, resolve_func
from cordelia.registry import data

def emit_instr_name(instrument):
	name = instrument.identity.name
	if name in tracker.instrument:
		return True
	tracker.instrument.add(name)

	instr_data = data['instrument'].get(name)
	match instr_data['kind']:
		case 'orc':
			path = instr_data['path']
			instr_orc = Path(path).read_text()
		case 'wav':
			template_stem_name = instr_data['template_stem']
			header_template = JINJA_SONVS_TEMPLATE_ENV.get_template(f'__header.j2')
			instr_orc = header_template.render(
				instrument=instrument,
				data=instr_data
			)
			instr_template = JINJA_SONVS_TEMPLATE_ENV.get_template(f'{template_stem_name}.j2')
			instr_orc += instr_template.render(
				name=instrument.identity.name,
			)

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
	if stage == QualityStage.REFERENCE and instrument.status == Status.UNPATCHED:
		print(f'SKIPPED for {stage} {instrument}')
		return
	for quality in instrument.verses:
		for _quality_name, plugins in registry_quality.items():
			for _name, module in plugins.items():
				if not module.get('stage') == stage:
					continue
				if module['match'](quality.items):
					logger.debug(f'MATCHED {_name} for {_quality_name} QUALITIY')
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
		for quality, keyword_path_map in DATA_TO_LOAD.items():
			if token in keyword_path_map:
				is_named_token = any(c.isalpha() for c in token)
				local_tracker = getattr(tracker, quality)
				if is_named_token and token not in local_tracker:
					match quality:
						case 'env':
							match keyword_path_map[token]['kind']:
								case 'orc':
									with open(keyword_path_map[token]['path']) as f:
										orc_queue.put(quality, f.read())
									local_tracker.add(token)
								case 'wav':
									path = keyword_path_map[token]['path']
									ftgen = f'gi{token} ftgen 0, 0, gienvdur, 1, "{path}", 0, 0, 0'
									orc_queue.put(quality, ftgen)
									local_tracker.add(token)
						case _:
							with open(keyword_path_map[token]) as f:
								orc_queue.put(quality, f.read())
							local_tracker.add(token)