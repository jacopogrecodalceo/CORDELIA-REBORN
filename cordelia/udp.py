from dataclasses import dataclass, field
import select
import socket

from cordelia.const import UDP_SIZE


@dataclass(slots=True)
class UDPRouter:
   ports: dict[int, str]
   socket_map: dict[socket.socket, str] = field(default_factory=dict)

   def open_ports(self) -> None:
      for port, name in self.ports.items():
         sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
         sock.bind(("127.0.0.1", port))

         self.socket_map[sock] = name

         print(f"OPEN {name} @ {port}")

   def close_ports(self) -> None:
      for sock in self.socket_map:
         sock.close()
      self.socket_map.clear()

   def receive_once(self, timeout: float = 0.0) -> list[tuple[str, str]]:
      readable, _, _ = select.select(
         list(self.socket_map),
         [],
         [],
         timeout
      )

      messages = []

      for sock in readable:
         payload, _ = sock.recvfrom(UDP_SIZE)

         if not payload:
            continue

         messages.append(
            (
               self.socket_map[sock],
               payload.decode("utf-8"),
            )
         )

      return messages
   
   
import threading
from queue import Queue


class UDPWorker:
   def __init__(self, router):
      self.router  = router
      self.queue   = Queue()
      self._stop   = threading.Event()
      self.thread  = threading.Thread(target=self._run, daemon=True)

   def start(self):
      self.router.open_ports()
      self.thread.start()

   def stop(self):
      self._stop.set()
      self.router.close_ports()

   def _run(self):
      while not self._stop.is_set():
         for direction, msg in self.router.receive_once(0.1):
            self.queue.put_nowait((direction, msg))

   def get(self, timeout=None):
      try:
         return self.queue.get(timeout=timeout)
      except Exception:
         return None