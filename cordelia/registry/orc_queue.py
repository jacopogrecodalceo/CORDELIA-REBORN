from cordelia.const import csound_comment_line
from datetime import datetime
import queue

class OrchestraQueue:
	_sections: list[str] = ['variable', 'env', 'instrument', 'modifier', 'score']

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

orc_queue = OrchestraQueue()
