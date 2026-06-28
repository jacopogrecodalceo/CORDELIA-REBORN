from datetime import datetime
import threading
import queue

from lark import logger

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

class Tracker:
	def __init__(self):
		self._trackers: set[str] = set()
		self._lock: threading.Lock = threading.Lock()

	def add(self, name: str) -> None:
		with self._lock:
			self._trackers.add(name)

	def remove(self, name: str) -> None:
		with self._lock:
			self._trackers.discard(name)

	def has(self, name: str) -> bool:
		with self._lock:
			return name in self._trackers

	def get(self) -> set[str]:
		with self._lock:
			return set(self._trackers)

	def clear(self) -> None:
		with self._lock:
				self._trackers.clear()

	def count(self) -> int:
		with self._lock:
			return len(self._trackers)

class OrchestraManager:
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
			'; ' + '·'*128,
			f'; BEGIN ORC | {now}',
			'; ' + '·'*128
		]
  
		if self.init:
			lines += [
				'schedule "heart", 0, -1'
			]
			self.init = False
  
		for s in self._sections:
			lines.extend(self._drain(self._queues[s]))
		lines.extend([
			'; ' + '·'*128,
			f'; END ORC | {now}',
			'; ' + '·'*128
		])
		return '\n'.join(lines)


stop_event = threading.Event()

# Module-level singletons
ft_pool = FtPool()

uid_tracker = {}

tracker = {
	'instrument': set(),
	'ft': set(),
	'modifier': set()
}   

orchestra_manager = OrchestraManager()
