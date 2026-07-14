from dataclasses import dataclass, field

class Pool:
	def __init__(self, start):
		self.start = start
		self._next: int = start
		self.used: set[int] = set()

	def _first_free(self, start: int) -> int:
		n = start
		while n in self.used:
			n += 1
		return n

	def alloc(self) -> int:
		n = self._first_free(self.start)   # search from the true floor, not just the high-water mark
		self.used.add(n)
		self._next = max(self._next, n + 1)
		return n

	def release(self, n: int) -> None:
		self.used.discard(n)

	def is_used(self, n: int) -> bool:
		return n in self.used

	def next_free(self) -> int:
		return self._first_free(self._next)

@dataclass
class PoolManager:
	ft: Pool = field(default_factory=lambda: Pool(1001))
	clear_instr: Pool = field(default_factory=lambda: Pool(1))


pool = PoolManager()
