import time

from cordelia.const import UDP_PORTS, QUERY_UDP_SLEEP_TIME
from cordelia.console import console
from cordelia.pipeline.parser import parse

from cordelia.udp import UDPRouter, UDPWorker
import cordelia.pipeline.qualities

if __name__ == "__main__":
   cordelia.pipeline.qualities.load()
   worker = UDPWorker(UDPRouter(UDP_PORTS))
   worker.start()

   print("LISTENING...")

   while True:
      item = worker.get(timeout=0.5)

      if not item:
         time.sleep(QUERY_UDP_SLEEP_TIME)
         continue

      direction, msg = item

      print(direction)
      print(msg)

      units = parse(msg)

      for u in units:
         console.print(u)