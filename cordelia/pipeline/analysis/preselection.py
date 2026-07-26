from cordelia.models.nodes import Node
from cordelia.errors import CordeliaValidationError
from cordelia.models.nodes import *


def _dedupe(nodes: list) -> dict[str, Node]:
	seen: dict[str, Node] = {}
	for node in nodes:
		if node.identity.uid in seen:
			#raise CordeliaValidationError(f"duplicate uid in this message: '{uid}'")
			node.identity.voice_id += 1
			node.identity.make()
		seen[node.identity.uid] = node
	return seen

previous = {}

def compare(current_nodes: list) -> None:
	global previous
	current = _dedupe(current_nodes)

	init_keys = current.keys() - previous.keys()
	release_keys = previous.keys() - current.keys()
	common_keys = current.keys() & previous.keys()

	results = []
	for uid in init_keys:
		node = current[uid]
		node.status = Status.INIT
		previous[uid] = node
		results.append(node)

	for uid in release_keys:
		node = previous.pop(uid)
		node.status = Status.RELEASE
		results.append(node)

	for uid in common_keys:
		node = current[uid]
		prior = previous[uid]
		if node != prior:
			node.status = Status.PATCHED
		else:
			node.status = Status.UNPATCHED
		node.prev_state = prior
		previous[uid] = node
		results.append(node)

	return results