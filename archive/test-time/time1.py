import ctcsound
import threading
import time

cs = ctcsound.Csound()
cs.setOption("-odac")
cs.compileOrc("""
sr     = 48000
ksmps  = 32
nchnls = 2
0dbfs  = 1

	instr 1
icps = p4
print icps
aout oscili .5, icps
aenv linseg 0, .005, 1, p3 - .005, 0
aout *= aenv
outall aout
	endin
""")
cs.start()

# performance thread — csound must be performing to process events
def perform():
   while cs.performKsmps() == 0:
      pass

perf_thread = threading.Thread(target=perform, daemon=True)
perf_thread.start()

# wait for csound to be ready
time.sleep(1/24)

def euclidean(pulses, steps):
   """generate euclidean rhythm as list of 0s and 1s"""
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

def send_cycle(start_time, duration, pattern, pitch=440):
   """send one cycle of events to csound with absolute timestamps"""
   step_dur = duration / len(pattern)
   for i, hit in enumerate(pattern):
      if hit:
         onset = i * step_dur
         print(onset)
         cs.scoreEvent("i", [1, onset, step_dur * .75, pitch])

def run():
   cycle_dur = 2.0
   pattern = euclidean(4, 8)
   t = cs.scoreTime()

   while True:
      send_cycle(t, cycle_dur, pattern)
      t += cycle_dur
      time.sleep(cycle_dur * 0.9)

clock_thread = threading.Thread(target=run, daemon=True)
clock_thread.start()

input("press enter to stop\n")
cs.stop()