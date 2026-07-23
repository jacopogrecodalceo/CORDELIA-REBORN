from __future__ import annotations

from functools import singledispatch
from cordelia.models.types import Status
from loguru import logger

from cordelia.models.nodes import Instrument, Variable
from cordelia.pipeline.conversion.runtime import InstrumentRuntime, VariableRuntime

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


def convert(runtime: InstrumentRuntime | VariableRuntime):
	status = runtime.node.status

	uid = runtime.node.identity.uid

	match status:
		case Status.RELEASE:
			session_registry.get(uid).release()
			session_registry.remove(uid)
		case Status.PATCHED:
			session_registry.get(uid).patch(runtime)
		case Status.INIT:
			runtime.init()
			session_registry.add(uid, runtime)

@singledispatch
def offer_one(node) -> None:
	pass


@offer_one.register
def _(node: Instrument) -> None:
	runtime = InstrumentRuntime(node)
	return runtime

@offer_one.register
def _(node: Variable) -> None:
	runtime = VariableRuntime(node)
	return runtime

def offer(nodes: list) -> None:
	for node in nodes:
		runtime = offer_one(node)
		convert(runtime)
