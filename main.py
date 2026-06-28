"""
main.py — cordelia runtime
===========================

THREAD ARCHITECTURE
-------------------

	main thread
		├── csound performance thread   (audio, highest priority)
		├── udp thread                  (network I/O, blocking recv)
		├── scheduler thread            (phase polling, sends to csound)
		└── csound monitor thread       (watchdog, triggers shutdown)

COMMUNICATION
-------------
	udp thread → parse → process → OrchestraManager queues
	scheduler thread → OrchestraManager.flush() → cs.compileOrc()
	csound monitor → stop_event → all threads
"""

import time
import signal
import threading
import ctcsound

from loguru import logger

import cordelia.pipeline.processor.instrument.score
import cordelia.pipeline.processor.run
import cordelia.pipeline.post_processor
import cordelia.csound_conversion.instrument_class
import cordelia.registry

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


# ─── CSOUND ───────────────────────────────────────────────────────────────────

def _build_csound() -> tuple[ctcsound.Csound, ctcsound.CsoundPerformanceThread]:
	init()
	cs = ctcsound.Csound()
	for f in flags:
		cs.setOption(f)
	orc = build_orchestra()
	if cs.compileOrcAsync(orc) != 0:
		raise RuntimeError("orchestra compilation failed")
	cs.start()
	pt = ctcsound.CsoundPerformanceThread(cs.csound())
	pt.play()
	time.sleep(SHORT_REST_AFTER_INIT)
	logger.info("csound | ready")
	return cs, pt


# ─── THREADS ──────────────────────────────────────────────────────────────────

def _udp_thread_fn(worker: UDPWorker) -> None:
	"""
	blocking UDP listener.
	parses incoming messages, runs the full pipeline.
	OrchestraManager queues are filled here as a side effect of convert().
	never touches csound directly.
	"""
	logger.info("udp | listening")
	while not cordelia.registry.stop_event.is_set():
		item = worker.get(timeout=0.5)
		if not item:
			continue
		direction, msg = item
		logger.debug(f"udp | {direction} | {msg!r}")
		try:
			units = parse(msg)
			for u in units:
				logger.debug(f"STARTING PROCESS: {u}")
				cordelia.pipeline.processor.run.process(u)
				logger.debug(f"STARTING POST PROCESS: {u}")
				cordelia.pipeline.post_processor.run(u)
				logger.debug(f"STARTING CONVERSION: {u}")
				cordelia.csound_conversion.instrument_class.convert(u)
		except Exception as e:
			logger.error(f"udp | pipeline error: {e}")


def _scheduler_thread_fn(cs: ctcsound.Csound, pt: ctcsound.CsoundPerformanceThread) -> None:
	"""
	phase-based scheduler.
	flushes OrchestraManager queues and sends compiled orc to csound.
	"""
	logger.info("scheduler | ready")
	while not cordelia.registry.stop_event.is_set():
		if cordelia.registry.orchestra_manager.filled:
			orc = cordelia.registry.orchestra_manager.flush()
			logger.debug(f"scheduler | compiling orc block")
			console.print(orc)
			cs.compileOrcAsync(orc)
		time.sleep(QUERY_UDP_WHILE_SLEEP_TIME)


def _csound_monitor_fn(pt: ctcsound.CsoundPerformanceThread) -> None:
	"""
	watchdog: blocks until csound stops, then triggers global shutdown.
	"""
	pt.join()
	logger.info("csound stopped — triggering shutdown")
	cordelia.registry.stop_event.set()


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main() -> None:

	cordelia.pipeline.processor.instrument.score.load()

	cs, pt = _build_csound()

	worker = UDPWorker(UDPRouter(UDP_PORTS))
	worker.start()

	threads = [
		threading.Thread(target=_csound_monitor_fn, args=(pt,),      daemon=True, name="csound_monitor"),
		threading.Thread(target=_udp_thread_fn,      args=(worker,),  daemon=True, name="udp"),
		threading.Thread(target=_scheduler_thread_fn, args=(cs, pt),  daemon=True, name="scheduler"),
	]
	for t in threads:
		t.start()
		logger.info(f"thread | started: {t.name}")

	def _shutdown(sig, frame) -> None:
		logger.info("shutdown | signal received")
		cordelia.registry.stop_event.set()

	signal.signal(signal.SIGINT, _shutdown)

	while not cordelia.registry.stop_event.is_set():
		time.sleep(1/8)

	logger.info("shutdown | cleaning up")
	worker.stop()
	pt.stop()
	pt.join()
	cs.stop()
	logger.info("bye")


if __name__ == "__main__":
	main()