import ctcsound
import threading
import queue
import time
from dataclasses import dataclass

cs = ctcsound.Csound()
cs.setOption("-odac")
cs.compileOrc("""
sr     = 48000
ksmps  = 32
nchnls = 2
0dbfs  = 1

instr 1
   icps = p4
   aout oscili .5, icps
   aenv linseg 0, .005, 1, p3 - .005, 0
   aout *= aenv
   outall aout/4
endin
""")
cs.start()

# CsoundPerformanceThread handles audio in its own thread
pt = ctcsound.CsoundPerformanceThread(cs.csound())
pt.play()
time.sleep(0.1)

def euclidean(pulses, steps):
   pattern = []
   bucket  = 0
   for _ in range(steps):
      bucket += pulses
      if bucket >= steps:
         bucket -= steps
         pattern.append(1)
      else:
         pattern.append(0)
   return pattern

@dataclass
class Voice:
   pattern:      list[int]
   cycle_dur:    float
   pitch:        float
   next_cs_time: float = 0.0

LOOKAHEAD = 2.0

voices = [
   Voice(euclidean(8, 8), 2.0, 440),
   Voice(euclidean(4, 8), 2.0, 660),
   Voice(euclidean(6, 8), 2.0, 880),
   Voice(euclidean(8, 8), 6, 220),
   Voice(euclidean(8, 8), 8, 330),
]

stop_event = threading.Event()

def scheduler():
   """
   runs on its own thread.
   uses cs.scoreTime() as reference — no python clock involved.
   sends events via pt.scoreEvent which is thread safe.
   sleeps for a fraction of a cycle to avoid busy waiting.
   """
   # wait until csound is producing audio
   while cs.scoreTime() < 0.01:
      time.sleep(0.01)

   for v in voices:
      v.next_cs_time = cs.scoreTime()

   while not stop_event.is_set():
      now = cs.scoreTime()
      for v in voices:
         while v.next_cs_time < now + LOOKAHEAD:
            step_dur = v.cycle_dur / len(v.pattern)
            for i, hit in enumerate(v.pattern):
               if hit:
                  onset = v.next_cs_time + i * step_dur
                  pt.scoreEvent(1, "i", [1, onset, step_dur, v.pitch])
            v.next_cs_time += v.cycle_dur
      # sleep for a small fraction of cycle — much less than lookahead
      time.sleep(v.cycle_dur * 1/24)

sched_thread = threading.Thread(target=scheduler, daemon=True)
sched_thread.start()

input("press enter to stop\n")
stop_event.set()
pt.stop()
cs.stop()