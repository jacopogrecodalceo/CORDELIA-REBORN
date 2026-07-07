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

from cordelia.pipeline.deducer import load_qualities_from_corpus
from cordelia.csound.run import build_orchestra, init
from cordelia.pipeline.parser import parse
from cordelia.pipeline.transformer import transform
from cordelia.pipeline.resolver import resolve
from cordelia.pipeline.converter import convert
from cordelia.udp import UDPRouter, UDPWorker
from cordelia.console import console
from cordelia.const import (
	SHORT_REST_AFTER_INIT,
	UDP_PORTS,
	QUERY_UDP_WHILE_SLEEP_TIME,
)
from config.options import flags
from cordelia.runtime import stop_event, orc_queue, session_units


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
	global session_units
	"""
	blocking UDP listener.
	parses incoming messages, runs the full pipeline.
	OrchestraManager queues are filled here as a side effect of convert().
	never touches csound directly.
	"""
	logger.info("udp | listening")
	while not stop_event.is_set():
		item = worker.get(timeout=.5)
		if not item:
			continue
		direction, msg = item
		logger.debug(f"udp | {direction} | {msg!r}")
		try:
			current_units = dict()
			temp_units = list()
			parsed_units = parse(msg)
			trees = transform(parsed_units)
			for unit in trees:
				logger.debug(f"BEGIN PROCESS: {unit}")
				resolve(unit)
				unit.score.process()
				current_units[unit.uid] = unit

			# compare units
			init_units = current_units.keys() - session_units.keys()
			release_units = session_units.keys() - current_units.keys()
			common_units = current_units.keys() & session_units.keys()

			for k in init_units:
				current_units[k].state = 'init'
				temp_units.append(current_units[k])
				session_units[k] = current_units[k]

			for k in release_units:
				session_units[k].state = 'release'
				temp_units.append(session_units[k])
				del session_units[k]
    
			for k in common_units:
				if current_units[k] != session_units[k]:
					current_units[k].state = 'patched'
					current_units[k].is_playing_instr = session_units[k]
					temp_units.append(current_units[k])

				else:
					current_units[k].state = 'unpatched'
					current_units[k].is_playing_instr = session_units[k]
					temp_units.append(current_units[k])

			convert(temp_units)


		except Exception as e:
			logger.exception(f"udp | pipeline error: {e}")


def _scheduler_thread_fn(cs: ctcsound.Csound, pt: ctcsound.CsoundPerformanceThread) -> None:
	"""
	phase-based scheduler.
	flushes OrchestraManager queues and sends compiled orc to csound.
	"""
	logger.info("scheduler | ready")
	while not stop_event.is_set():
		if orc_queue.filled:
			orc = orc_queue.flush()
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
	stop_event.set()


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main() -> None:

	load_qualities_from_corpus()

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
		stop_event.set()

	signal.signal(signal.SIGINT, _shutdown)

	while not stop_event.is_set():
		time.sleep(1/8)

	logger.info("shutdown | cleaning up")
	worker.stop()
	pt.stop()
	pt.join()
	cs.stop()
	logger.info("bye")


if __name__ == "__main__":
	main()