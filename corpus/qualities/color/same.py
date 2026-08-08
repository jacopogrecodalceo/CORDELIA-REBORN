import re
from corpus.qualities import *
from cordelia.models.types import QualityStage

stage = QualityStage.REFERENCE

def match(items: list) -> bool:
	if items[0] == 'same' and items[2] == 'as':
		if items[1] == 'color' or items[1] == 'col':
			return True
	return False

def main(args):
	items = args.quality.items[3:]
	nodes = args.nodes

	target_instr_uid = items[0]
	target_instr = None
	if not re.search(r'_\d+$', target_instr_uid):
		target_instr_uid += '_1'
	for node in nodes:
		if target_instr_uid == node.identity.uid:
			target_instr = node

	if target_instr is None:
		CordeliaDeductionError('no same as found')

	for quality_name in ['color']:
		for q in getattr(target_instr, quality_name):
			getattr(args.instrument, quality_name).copy(q)




