import ctcsound
import time
from dataclasses import dataclass

cs = ctcsound.Csound()
cs.setOption("-odac")
cs.setOption("-d")
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

# --- The key difference: create the performance thread ---
# Note: cs.csound() returns the underlying Csound instance pointer
pt = ctcsound.CsoundPerformanceThread(cs.csound())
pt.play()  # Start the audio thread

# Let Csound stabilize
time.sleep(1/8)

# --- Euclidean generator (same as before) ---
def euclidean(pulses, steps):
	talea = []
	bucket = 0
	for _ in range(steps):
		bucket += pulses
		if bucket >= steps:
				bucket -= steps
				talea.append(1)
		else:
				talea.append(0)
	return talea

@dataclass
class Staff:
	instrument: int
	talea: list[int]
	colores: list[float]
	dur: float
	next_cycle_start: float = 0.0

 

staves = [
	Staff(1, euclidean(8, 8), [440], 2),
	Staff(1, euclidean(4, 8), [330], 2),
]

# Initialize with Csound's current time
for v in staves:
	v.next_cycle_start = cs.scoreTime()

# --- Scheduler thread (much simpler now!) ---
def scheduler_fn():
	while True:
		now_cs = cs.scoreTime()
		
		for staff in staves:
				while staff.next_cycle_start <= now_cs + .5:
					step_dur = staff.dur / len(staff.talea)
					
					for i, hit in enumerate(staff.talea):
						if hit > 0:
								event_onset = staff.next_cycle_start + i * step_dur
								# Thread-safe event scheduling!
								# Note: first parameter 0 means absolute time
								pt.scoreEvent(1, "i", (staff.instrument, event_onset, step_dur, 440))
					
					staff.next_cycle_start += staff.dur
		
				time.sleep(1/24)

# Run scheduler in its own thread
import threading
sched_thread = threading.Thread(target=scheduler_fn, daemon=True)
sched_thread.start()

print("Playing - press Enter to stop")
input()

# Clean shutdown
pt.stop()
pt.join()
cs.stop()