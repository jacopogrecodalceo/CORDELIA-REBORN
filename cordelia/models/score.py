from loguru import logger
from dataclasses import dataclass, field, fields
from typing import Any

from cordelia.const import data_to_emit
from cordelia.runtime import tracker, orc_queue

import operator

_OPS = {
	'+': operator.add,
	'-': operator.sub,
	'*': operator.mul,
	'/': operator.truediv,
	'=': None,
}

def auto_config(*classes):
	def decorator(func):
		def wrapper(args):
			results = func(args)
			instrument = args.instrument

			if len(classes) == 1:
				attr_name = classes[0].__name__.lower()
				getattr(instrument.score, attr_name).append(classes[0](results))
				return results

			for values, cls in zip(results, classes):
				attr_name = cls.__name__.lower()
				getattr(instrument.score, attr_name).append(cls(values))
			return results
		return wrapper
	return decorator

	
@dataclass
class SharedQuality:
	from_corpus: Any
	_values: list[Any] = field(default_factory=list, init=False)
	dirty: bool = False  # Move dirty after _values

	@property
	def values(self) -> list[Any]:
		return self._values
	
	@values.setter
	def values(self, new_values: list[Any]):
		if self._values != new_values:
			self._values = new_values
			self.dirty = True
	
@dataclass
class Cycle(SharedQuality):
	def process(self):
    
		return [self.from_corpus]

@dataclass
class Talea(SharedQuality):
	def process(self):
		return self.from_corpus

@dataclass
class Colores(SharedQuality):
	def process(self):
		return self.from_corpus

@dataclass
class Dur(SharedQuality):
	def process(self):
		return self.from_corpus

@dataclass
class Dyn(SharedQuality):	
	def process(self):
		return self.from_corpus

@dataclass
class Env(SharedQuality):
	def process(self):
		return self.from_corpus

@dataclass
class Space(SharedQuality):
	def process(self):
		return self.from_corpus

@dataclass
class Character(SharedQuality):
	def process(self):
		return self.from_corpus


def count_ones(talea: list) -> list:
	count = 1
	for i, v in enumerate(talea):
		if int(v) > 0:
			talea[i] = count
			count += 1
	return talea


def make_durs_from_talea(talea: list) -> list:
	durs = []
	count = 1
	for value in reversed(talea):
		if value == 0:
			count += 1
		else:
			durs.append(count)
			count = 1
	durs.reverse()
	durs[-1] += count - 1
	return durs

@dataclass
class Score:
	talea: list[Talea] = field(default_factory=list)
	colores: list[Colores] = field(default_factory=list)
	dur: list[Dur] = field(default_factory=list)
	dyn: list[Dyn] = field(default_factory=list)
	env: list[Env] = field(default_factory=list)
	space: list[Env] = field(default_factory=list)
	character: list[Character] = field(default_factory=list)
	cycle: list[Cycle] = field(default_factory=list)

	def __iter__(self):
		for f in fields(self):
			yield f.name, getattr(self, f.name)

	def flat_values(self):
		for quality_name in vars(self):
			new_values = []
			for class_value in getattr(self, quality_name):
				new_values.extend(class_value.process())
			setattr(self, quality_name, new_values)

	def load_others(self):
		score_tokens = (
			token
			for quality_name in vars(self)
			for token in getattr(self, quality_name)
		)
		for token in score_tokens:
			for quality_name, keyword_path_map in data_to_emit.items():
				if token in keyword_path_map:
					is_named_token = any(c.isalpha() for c in token)

					local_tracker = getattr(tracker, quality_name)
					if is_named_token and token not in local_tracker:
						with open(keyword_path_map[token]) as f:
							orc_queue.put(quality_name, f.read())
						local_tracker.add(token)
      
	def fill_default(self):
		if not self.colores:
			self.colores = [1]
		if not self.dur:
			self.dur = [1]
		if not self.dyn:
			self.dyn = ['mf']
		if not self.env:
			self.env = ['cls']
		if not self.cycle:
			self.cycle = [8]
		if not self.space:
			self.space = [0]

	def process_talea(self):
		self.talea = count_ones(self.talea)

	""" def process_cycle(self):
		full_cycle = []
		cycle_n = len(self.cycle)
		for i in range(64):
			full_cycle.append(self.cycle[i%cycle_n])
		self.cycle = full_cycle """
	
	def process_cycle(self):
		pass

	def process_dur(self):
		deducted_durs = self.dur
		talea_durs = make_durs_from_talea(self.talea)
  
		if 'dur' not in deducted_durs:
			self.dur = talea_durs
			return

		index_dur = deducted_durs.index('dur')
		op_symbol = deducted_durs[index_dur + 1]
		dur_values = deducted_durs[index_dur + 2:]
		if isinstance(dur_values[0], list):
			dur_values = dur_values[0]

		if op_symbol == '=':
			self.dur = dur_values
		else:
			op = _OPS[op_symbol]
			self.dur = [
				op(float(talea_dur), float(dur_values[i % len(dur_values)]))
				for i, talea_dur in enumerate(talea_durs)
			]

	def process_dyn(self):
		for i, value in enumerate(self.dyn):
			self.dyn[i] = rf'${value}'

	def process_env(self):
		for i, value in enumerate(self.env):
			self.env[i] = f'gi{value}'

	def process(self):
		self.flat_values()
		self.fill_default()

		self.load_others()
  
		self.process_talea()
		self.process_cycle()
		self.process_dur()
		self.process_dyn()
		self.process_env()
  

# ---------------------------------------------------------------------------- #
#                                AYATTETION HERE                               #
# ---------------------------------------------------------------------------- #
	def deduce_func(self):
		from cordelia.models.ast import Func  # deferred import breaks the cycle
		from cordelia.pipeline.deducer import func_registry
		for quality_name in vars(self):
			tokens = getattr(self, quality_name)
			new_tokens = []
			for token in tokens:
				print(token)
				if isinstance(token, Func):
					name  = token.name
					items = token.args
					fn = func_registry.get(name)
					if fn is None:
						raise ValueError(
							f"cannot find function '{name}', available: {', '.join(sorted(func_registry))}"
						)
					new_tokens.append(fn(items))
				else:
					new_tokens.append(token)
			setattr(self, quality_name, new_tokens)
