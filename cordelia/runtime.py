from cordelia.const import csound_comment_line
from datetime import datetime
from dataclasses import dataclass, field
import threading
import queue

class FtPool:
	def __init__(self, start: int = 1001):
		self._next: int = start
		self.used: set[int] = set()

	def alloc(self) -> int:
		while self._next in self.used:
				self._next += 1
		n = self._next
		self.used.add(n)
		self._next += 1
		return n

	def release(self, n: int) -> None:
		self.used.discard(n)

	def is_used(self, n: int) -> bool:
		return n in self.used

	def next_free(self) -> int:
		n = self._next
		while n in self.used:
				n += 1
		return n


class OrchestraQueue:
	_sections: list[str] = ['variable', 'ft', 'instrument', 'modifier', 'score']

	def __init__(self):
		self.init = True
		self._queues: dict[str, queue.Queue[str]] = {
			s: queue.Queue() for s in self._sections
		}

	def put(self, section: str, value: str) -> None:
		self._queues[section].put(value)

	@property
	def filled(self) -> bool:
		return any(not q.empty() for q in self._queues.values())

	def _drain(self, q: queue.Queue[str]) -> list[str]:
		items = []
		while True:
			try:
				items.append(q.get_nowait())
			except queue.Empty:
				break
		return items

	def flush(self) -> str:
		now = datetime.now().strftime("%I·%M%p").lower()
		lines = [
			csound_comment_line(f'BEGIN ORC | {now}'),
		]
  
		if self.init:
			lines += [
				'schedule "heart", 0, -1'
			]
			self.init = False
  
		for s in self._sections:
			lines.extend(self._drain(self._queues[s]))
		lines.append(csound_comment_line(f'END ORC | {now}'))
		return '\n'.join(lines)


stop_event = threading.Event()


@dataclass
class CompilerQueue:
	instrument: OrchestraQueue = field(default_factory=OrchestraQueue)
	modifier: OrchestraQueue = field(default_factory=OrchestraQueue)
	ft: OrchestraQueue = field(default_factory=OrchestraQueue)
	mode: OrchestraQueue = field(default_factory=OrchestraQueue)
	scala: OrchestraQueue = field(default_factory=OrchestraQueue)

@dataclass
class Tracker:
	instrument: set = field(default_factory=set)
	modifier: dict = field(default_factory=dict)
	ft: set = field(default_factory=set)
	mode: set = field(default_factory=set)
	scala: set = field(default_factory=set)

tracker = Tracker()
orc_queue = CompilerQueue()
ft_pool = FtPool()
