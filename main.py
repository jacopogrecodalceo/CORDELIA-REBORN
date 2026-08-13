""" import os
import sys

if not os.environ.get("CORDELIA_MALLOC_DEBUG"):
	env = os.environ.copy()
	env.update({
		"MallocScribble": "1",
		"MallocPreScribble": "1",
		"MallocGuardEdges": "1",
		"MallocErrorAbort": "1",
		"CORDELIA_MALLOC_DEBUG": "1",
	})
	os.execve(sys.executable, [sys.executable] + sys.argv, env) """

import time
import signal
import threading
import ctcsound

from loguru import logger

from cordelia.csound.run import build_orchestra, init

from cordelia.const import OUTPUT_SCORE_PATH
from cordelia.pipeline import compile
from cordelia.udp import UDPRouter, UDPWorker
from cordelia.console import console

from cordelia.const import (
	SHORT_REST_AFTER_INIT,
	QUERY_UDP_WHILE_SLEEP_TIME,
	UDP_PORTs,
)
from cordelia.helpers import fix_wav_header
from config.options import flags
from cordelia.registry import orc_queue

stop_event = threading.Event()

# ─── CSOUND ───────────────────────────────────────────────────────────────────

def _build_csound() -> tuple[ctcsound.Csound, ctcsound.CsoundPerformanceThread]:
	init()
	cs = ctcsound.Csound()

	cs.createMessageBuffer(toStdOut=False)

	for f in flags:
		cs.setOption(f)
		print(f)
	orc = build_orchestra()
	print(orc)
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
	logger.info("udp | listening")
	while not stop_event.is_set():
		item = worker.get(timeout=.5)
		if not item:
			continue
		direction, message = item
		logger.debug(f"udp | {direction} | {message!r}")
		if direction == 'CORDELIA':
			try:
				compile(message)
			except Exception as e:
				logger.exception(f"udp | pipeline error: {e}")
		if direction == 'CSOUND':
			orc_queue.put('score', message)


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
	pt.join()
	logger.info("csound stopped — triggering shutdown")
	stop_event.set()

def _record(pt: ctcsound.CsoundPerformanceThread) -> None:
	pt.record(str(OUTPUT_SCORE_PATH), 24, 16) 

def _csound_log_thread_fn(cs: ctcsound.Csound) -> None:
	while not stop_event.is_set():
		while cs.messageCnt() > 0:
			msg = cs.firstMessage()
			logger.debug(f"csound | {msg.rstrip()}")
			cs.popFirstMessage()
		time.sleep(QUERY_UDP_WHILE_SLEEP_TIME)

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main() -> None:
	logger.add(
		f"{str(OUTPUT_SCORE_PATH)}.log",
		level="DEBUG",
		rotation="50 MB",
		retention="14 days",
		backtrace=True,
		diagnose=True,
	)
	cs, pt = _build_csound()

	worker = UDPWorker(UDPRouter(UDP_PORTs))
	worker.start()

	threads = [
		threading.Thread(target=_csound_monitor_fn, args=(pt,),			daemon=True, name="csound_monitor"),
		threading.Thread(target=_record, args=(pt,),							daemon=True, name="record_csound"),
		threading.Thread(target=_csound_log_thread_fn, args=(cs,), 		daemon=True, name="csound_log"),
		threading.Thread(target=_udp_thread_fn,      args=(worker,),	daemon=True, name="udp"),
		threading.Thread(target=_scheduler_thread_fn, args=(cs, pt),	daemon=True, name="scheduler"),
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
	pt.stopRecord()
	cs.stop()
	fix_wav_header(OUTPUT_SCORE_PATH)
	logger.info("bye")


if __name__ == "__main__":
	main()