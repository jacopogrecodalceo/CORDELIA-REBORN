from __future__ import annotations

from functools import singledispatch

from loguru import logger

from cordelia.models.instrument import Instrument
from cordelia.models.variable import Variable
from cordelia.runtime.instrument import InstrumentRuntime


class SessionRegistry:
	"""Tracks currently-playing instrument runtimes, keyed by uid."""

	def __init__(self):
		self._runtimes: dict[str, InstrumentRuntime] = {}

	def get(self, uid: str) -> InstrumentRuntime:
		return self._runtimes[uid]

	def add(self, uid: str, runtime: InstrumentRuntime) -> None:
		self._runtimes[uid] = runtime

	def remove(self, uid: str) -> None:
		del self._runtimes[uid]


session_registry = SessionRegistry()


def convert_instrument(runtime: InstrumentRuntime) -> None:
	state = runtime.instrument.state
	logger.debug(f'{state} {runtime.instrument}')

	uid = runtime.instrument.uid

	match state:
		case 'release':
			session_registry.get(uid).release()
			session_registry.remove(uid)
		case 'patched':
			session_registry.get(uid).patch(runtime)
		case 'init':
			runtime.init()
			session_registry.add(uid, runtime)
		case _:
			logger.debug(f'unpatched {runtime.instrument}')


@singledispatch
def offer_one(poem) -> None:
	pass


@offer_one.register
def _(poem: Instrument) -> None:
	runtime = InstrumentRuntime(instrument=poem)
	convert_instrument(runtime)


@offer_one.register
def _(poem: Variable) -> None:
	pass


def offer(poems: list) -> None:
	for poem in poems:
		offer_one(poem)