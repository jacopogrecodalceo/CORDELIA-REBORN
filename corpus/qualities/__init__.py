from cordelia.errors import *
from cordelia.models.types import QualityStage



def auto_config(*attrs):
	def decorator(func):
		def wrapper(args):			
			results = func(args)
			args.func = func

			if len(attrs) == 1:
				getattr(args.instrument, attrs[0]).add(results, args) #qualities[attr_name].add(ensure_list(results), args.quality)
				return results

			for attr_name, values in zip(attrs, results):
				getattr(args.instrument, attr_name).add(values, args) #qualities[attr_name].add(ensure_list(results), args.quality)
			return results
		return wrapper
	return decorator


