from loguru import logger
from archive.processor.instrument.score import load, _registry
load()

for category, plugins in _registry.items():
	for name, module in plugins.items():
		print(name, module)
		fn = getattr(module, 'main', None)
		logger.debug(fn)
		assert fn != None, f'NO MAIN IN {name} - {module}'
