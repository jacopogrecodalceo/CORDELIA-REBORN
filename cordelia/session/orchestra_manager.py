# queue_manager.py
import threading
from collections import deque
from typing import Any, List

class OrchestraQueue:
	def __init__(self):
		self._queue = deque()
		self._lock = threading.Lock()
	
	def add(self, item: Any) -> None:
		"""Add an item to the queue"""
		with self._lock:
			self._queue.append(item)
	
	def add_multiple(self, items: List[Any]) -> None:
		"""Add multiple items to the queue"""
		with self._lock:
			self._queue.extend(items)
	
	def get_and_clear(self) -> List[Any]:
		"""Get all items and clear the queue atomically"""
		with self._lock:
			items = list(self._queue)
			self._queue.clear()
			return items
	
	def get(self) -> List[Any]:
		"""Get all items without clearing"""
		with self._lock:
			return list(self._queue)
	
	def clear(self) -> None:
		"""Clear the queue"""
		with self._lock:
			self._queue.clear()

	def is_empty(self) -> bool:
		"""Check if queue is empty"""
		with self._lock:
			return len(self._queue) == 0

# Global instance
QUEUEs = {
 	'instr': OrchestraQueue(),
 	'mod': OrchestraQueue(),
 	'fts': OrchestraQueue(),
 	'modes': OrchestraQueue(),
 	'scala': OrchestraQueue(),
   }
