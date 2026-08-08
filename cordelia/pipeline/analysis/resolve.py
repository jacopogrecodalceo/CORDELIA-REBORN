from types import SimpleNamespace

from cordelia.pipeline.syntax.ast_builder import Expr, Func

from cordelia.registry import registry_func
from cordelia.errors import *

def deduce_function(instrument, func: Func):
	fn = registry_func.get(func.name, None)
	if fn:
		args = SimpleNamespace(instrument=instrument, items=func.items)
		return fn(args)

def resolve_func(instrument, items: list) -> list:
	"""Recursively parse and reduce all structures to strings/numbers"""
	result = []
	
	for item in items:
		if isinstance(item, Expr):
				# Process Expr items recursively
				processed = resolve_func(instrument, item.items)
				# Join as expression string
				expr_str = ''.join(str(x) for x in processed)
				result.append(expr_str)

		elif isinstance(item, Func):
				# Process Func items recursively
				processed_items = resolve_func(instrument, item.items)

				# Create new Func with processed items
				new_func = Func(item.name, processed_items)
				result.append(deduce_function(instrument, new_func))

		elif isinstance(item, list):
				# Recursively process list
				processed = resolve_func(instrument, item)
				result.extend(processed)
		else:
				result.append(item)
	
	return result

def resolve_expr(items):
	"""Recursively flatten items, expanding any Expr objects."""
	result = []
	for item in items:
		if isinstance(item, Expr):
			# Recursively flatten the Expr's items
			result.extend(resolve_expr(item.items))
		else:
			result.append(item)
	return result

