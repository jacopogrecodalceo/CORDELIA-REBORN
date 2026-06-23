"""
main.py — cordelia runtime
===========================

THREAD ARCHITECTURE
-------------------

	main thread
		├── csound performance thread   (audio, highest priority)
		├── udp thread                  (network I/O, blocking recv)
		├── scheduler thread            (phase polling, sends to csound)
		└── main thread                 (keepalive + graceful shutdown)

COMMUNICATION
-------------
	udp thread → queue → scheduler thread
	scheduler thread → csound performance thread (via pt.scoreEvent)
"""

import time
import queue
import signal
import threading
import ctcsound

from loguru import logger

import cordelia.pipeline.qualities
from cordelia.csound.run import build_orchestra, init
from cordelia.pipeline.parser import parse
from cordelia.udp import UDPRouter, UDPWorker
from cordelia.console import console
from cordelia.const import (
	SHORT_REST_AFTER_INIT,
	UDP_PORTS,
	QUERY_UDP_WHILE_SLEEP_TIME,
)
from config.options import flags

# ─── SHARED STATE ─────────────────────────────────────────────────────────────

# parsed units from UDP land here, scheduler consumes them
event_queue: queue.Queue = queue.Queue()

# signals all threads to stop
stop_event = threading.Event()


# ─── CSOUND ───────────────────────────────────────────────────────────────────

def build_csound() -> tuple[ctcsound.Csound, ctcsound.CsoundPerformanceThread]:
	init()

	cs = ctcsound.Csound()

	for f in flags:
		cs.setOption(f)

	orc    = build_orchestra()
	result = cs.compileOrcAsync(orc)
	if result != 0:
		raise RuntimeError("orchestra compilation failed")

	cs.start()

	pt = ctcsound.CsoundPerformanceThread(cs.csound())
	pt.play()

	time.sleep(SHORT_REST_AFTER_INIT)
	logger.info("csound ready")

	return cs, pt


# ─── UDP THREAD ───────────────────────────────────────────────────────────────

def udp_thread_fn(worker: UDPWorker):
	"""
	blocking UDP listener.
	parses incoming messages and puts units into event_queue.
	never touches csound directly.
	"""
	logger.info("udp | listening")

	while not stop_event.is_set():
		item = worker.get(timeout=0.5)

		if not item:
			continue

		direction, msg = item
		logger.debug(f"udp | {direction} | {msg!r}")

		try:
			units = parse(msg)
			for u in units:
				event_queue.put(u)
		except Exception as e:
			logger.error(f"udp | parse error: {e}")


# ─── SCHEDULER THREAD ─────────────────────────────────────────────────────────

def scheduler_thread_fn(cs: ctcsound.Csound, pt: ctcsound.CsoundPerformanceThread):
	"""
	phase-based scheduler.
	consumes units from event_queue and sends events to csound.
	sleeps between polls to avoid busy waiting.
	"""
	logger.info("scheduler | ready")

	while not stop_event.is_set():
		# drain the queue — apply any new units
		while not event_queue.empty():
			try:
				unit = event_queue.get_nowait()
				_apply_unit(unit, cs, pt)
			except queue.Empty:
				break

		# TODO: phase polling and event scheduling goes here

		time.sleep(QUERY_UDP_WHILE_SLEEP_TIME)

def csound_monitor_fn(pt: ctcsound.CsoundPerformanceThread):
	"""
	watches the csound performance thread.
	when csound stops, signals all other threads to stop.
	"""
	pt.join()   # blocks until csound performance thread exits
	logger.info("csound stopped — shutting down")
	stop_event.set()

def _apply_unit(unit, cs, pt):
	"""dispatch a parsed unit to the right handler"""
	logger.debug(f"scheduler | applying unit: {unit}")
	# TODO: dispatch to instrument/variable handlers


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
	# load quality plugins before anything else
	cordelia.pipeline.qualities.load()

	# build csound
	cs, pt = build_csound()

	# start udp
	worker = UDPWorker(UDPRouter(UDP_PORTS))
	worker.start()

	# start threads
	threads = [
		threading.Thread(target=csound_monitor_fn,    args=(pt,),        daemon=True, name="csound_monitor"),
		threading.Thread(target=udp_thread_fn,         args=(worker,),    daemon=True, name="udp"),
		threading.Thread(target=scheduler_thread_fn,   args=(cs, pt),     daemon=True, name="scheduler"),
	]
	for t in threads:
		t.start()
		logger.info(f"thread started: {t.name}")

	# graceful shutdown on ctrl+c
	def _shutdown(sig, frame):
		logger.info("shutting down...")
		stop_event.set()

	signal.signal(signal.SIGINT, _shutdown)

	# keep main thread alive
	while not stop_event.is_set():
		time.sleep(1/8)

	# cleanup
	worker.stop()
	pt.stop()
	pt.join()
	cs.stop()
	logger.info("bye")


if __name__ == "__main__":
	main()