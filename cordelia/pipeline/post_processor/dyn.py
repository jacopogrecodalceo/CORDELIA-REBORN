import cordelia.const

def __post_init__(self):
	for i, value in enumerate(self.values):
		if isinstance(value, str):
				try:
					self.values[i] = cordelia.const.data.file('dyns')[value]['norm']
				except ValueError:
					raise ValueError(value)
