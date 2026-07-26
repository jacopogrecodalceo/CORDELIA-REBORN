from lark import Tree
from lark.visitors import Visitor_Recursive
from cordelia.registry import data

class MacroExpander(Visitor_Recursive):
	"""Expands `repeat` nodes into repeated siblings, wherever they occur,
	bottom-up, before the transformer runs. No grammar coupling -- any
	future rule that can contain a repeat gets this for free."""

	def __default__(self, tree: Tree):
		children = []
		for child in tree.children:
			if isinstance(child, Tree) and child.data == "repeat":
				syllabe, *reps = child.children
				n = 1
				for t in reps:
					n *= int(str(t)[1:])
				children.extend([syllabe] * n)
			elif isinstance(child, Tree):
				child.children = [
					data['macro'][c] if c in data['macro'] else c
					for c in child.children
				]
				children.append(child)
			else:
				children.append(child)
		tree.children = children