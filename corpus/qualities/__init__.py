from cordelia.models.qualities import QUALITIEs
from cordelia.errors import *

class QualityBase:
	pass
		
for quality_name in QUALITIEs:
	globals()[quality_name.capitalize()] = type(quality_name, (), {})

def ensure_list(item):
	"""Convert item to list if it's not already a list"""
	if not isinstance(item, list):
		return [item]
	return item   

def auto_config(*classes):
	def decorator(func):
		def wrapper(args):			
			results = func(args)
			instrument = args.instrument

			if len(classes) == 1:
				attr_name = classes[0].__name__.lower()
				instrument.qualities[attr_name].add(ensure_list(results), args.quality)
				return results

			for values, cls in zip(results, classes):
				attr_name = cls.__name__.lower()
				instrument.qualities[attr_name].add(ensure_list(values), args.quality.items)
			return results
		return wrapper
	return decorator
