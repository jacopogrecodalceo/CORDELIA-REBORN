import ctcsound
import threading
import time
import queue
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

stop_event = threading.Event()
event_queue = queue.Queue()

# --- Performance thread ---
perf_ready = threading.Event()

def perf_thread_fn():
    perf_ready.set()
    
    while not stop_event.is_set():
        # Process events from queue
        try:
            while True:
                event = event_queue.get_nowait()
                # event = (start_time, duration, pitch)
                cs.scoreEventAbsolute("i", [1, event[0], event[1], event[2]], 0)
        except queue.Empty:
            pass
        
        if cs.performKsmps() != 0:
            break

def schedule_note(cs_time, duration, pitch):
    """Schedule a note from any thread"""
    event_queue.put((cs_time, duration, pitch))

# --- Euclidean generator ---
def euclidean(pulses, steps):
    pattern = []
    bucket = 0
    for i in range(steps):
        bucket += pulses
        if bucket >= steps:
            bucket -= steps
            pattern.append(1)
        else:
            pattern.append(0)
    return pattern

@dataclass
class Voice:
    pattern: list[int]
    cycle_dur: float
    pitch: float
    next_cycle_start: float = 0.0

# Start performance thread first
perf_thread = threading.Thread(target=perf_thread_fn, daemon=True)
perf_thread.start()
perf_ready.wait()
time.sleep(1/8)  # Let Csound stabilize

# Initialize voices with Csound's performance time (not score time)
voices = [
    Voice(euclidean(8, 8), 2.0, 440),
    Voice(euclidean(4, 8), 2.0, 660),
    Voice(euclidean(4, 9), 2.0, 880),
]

# Use cs.getScoreTime() - this always advances!
for v in voices:
    v.next_cycle_start = cs.scoreTime()

# --- Scheduler thread ---
def scheduler_fn():
    while not stop_event.is_set():
        # Get current Csound performance time
        now_cs = cs.scoreTime()
        
        for v in voices:
            # Schedule cycles that are due or coming up
            while v.next_cycle_start <= now_cs + 0.5:  # 500ms lookahead
                step_dur = v.cycle_dur / len(v.pattern)
                
                print(f"Scheduling cycle at {v.next_cycle_start:.3f}")  # Debug
                
                for i, hit in enumerate(v.pattern):
                    if hit:
                        note_time = v.next_cycle_start + i * step_dur
                        schedule_note(note_time, step_dur, v.pitch)
                
                v.next_cycle_start += v.cycle_dur
        
        # Small sleep to prevent CPU overload
        time.sleep(0.01)

sched_thread = threading.Thread(target=scheduler_fn, daemon=True)
sched_thread.start()

print("Playing - press Enter to stop")
input()
stop_event.set()
cs.stop()