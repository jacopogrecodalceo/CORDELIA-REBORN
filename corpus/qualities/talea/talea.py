from cordelia.pipeline.transformer import Quality
from cordelia.pipeline.deduction import deducer


class Talea:
	def __init__(self, talea_array):
		self._array = talea_array

	@staticmethod
	def _validate(array):
		for x in array:
			if x != 0 or x != 1:
				raise ValueError(array)
	
	@property
	def _array(self):
		self._validate(self._array)
		

@deducer
def talea(quality: Quality) -> Talea:
	if not quality.items or quality.items[0] != "talea":
		return None
	talea_array = [1, 1, 0]
	return Talea(talea_array)

