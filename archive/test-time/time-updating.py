from dataclasses import dataclass

import ctcsound
import time
import threading
import code

CHANNELs = 2

# Add this BEFORE creating your Csound instance
def getInstrumentNumber(self, name):
	"""Get instrument number using nstrnum opcode via evalCode"""
	try:
		channel = f"_tmp_insnum_{id(self)}_{abs(hash(name))}"
		code = f'''
		ins_num = nstrnum("{name}")
		chnset ins_num, "{channel}"
		'''
		self.evalCode(code)
		result, _ = self.controlChannel(channel)
		result = int(result)
		self.evalCode(f'chnclear "{channel}"')
		print(f"Instrument '{name}' = {result}")
		return result
	except Exception as e:
		print(f"Error getting instrument number: {e}")
		return -1

# Monkey-patch ctcsound
ctcsound.Csound.getInstrumentNumber = getInstrumentNumber

cs = ctcsound.Csound()
cs.setOption("-odac")
#cs.setOption("-o1.wav")
cs.setOption("-m0")
cs.setOption("-3")
orc = """

sr     = 48000
ksmps  = 32
nchnls = 2
0dbfs  = 1

	instr 1
kphase phasor 1/64;+jitter(.05, 1/8, 1/64)
	chnset kphase, "main_phase"
	endin
	alwayson(1)

	instr tinyosc

idur init p3
icps init p4
anoi fractalnoise 1/12+random(0, .005), 1
aosc oscil3 .5+random(-.005, .005), icps
avco vco2 1/64+random(0, .005), icps

aout sum aosc, anoi*cosseg(1, .005+random(.0095, .005), 0), avco

irel init idur+random(.005, -.005)
aout = aout * (.5 + oscil3:a(cossegr:a(0, idur, 1, idur, random(.25, .5), irel, 0)/4, 3+random(-.005, .005)))

	xtratim irel
aenv cossegr 0, .005, 1, idur - .005, random(1/8, 1/24), irel, 0
aout *= aenv
	outch p5, aout/3
	endin

"""

KSMPS = cs.ksmps()
SR = cs.sr()
QUERY_SLEEP_TIME = 1/64
result = cs.compileOrc(orc)
if result != 0:
	raise ValueError("ERROR in compiling the orchestra")

cs.start()

pt = ctcsound.CsoundPerformanceThread(cs.csound())
pt.play()
time.sleep(0.125)

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


# Now create your Csound instance and use it

@dataclass
class Phase:
   main: float = 0
   last: float = 0

class Staff:
	def __init__(self, instrument, talea, colores, dur):
		# main parameters
		self.instrument = instrument
		self.talea = talea  
		self.colores = colores
		self.dur = dur
		self._colores_count = 0
		self.instrument_num = cs.getInstrumentNumber(self.instrument)
		self.dirty = False
		self.phase = Phase()
		self.phases = []
		self.channel = 0
		self.make_phases()

	def make_phases(self):
		n = len(self.talea)
		self.phases = [i / n for i, hit in enumerate(self.talea) if hit] # [1,0,1,0,1,0,1,0] → [0.0, 0.25, 0.5, 0.75]

	def update(self, **kwargs):
		for key, value in kwargs.items():
				if hasattr(self, key):
					setattr(self, key, value)
					self.dirty = True

	@property
	def colores_count(self):
		result = self._colores_count
		self._colores_count += 1
		return result
		
	def send_event(self):	
		onset = 0
		dur = 1/12
		pitch = self.colores[self.colores_count % len(self.colores)]
		score = [self.instrument_num, onset, dur, pitch]
		if self.channel == 0:
			for ch in range(1, CHANNELs + 1):
				print(score)
				pt.scoreEvent(0, "i", score + [ch])
		else:
			#score_string = ' '.join(map(str, scores + [self.channel]))
			pt.scoreEvent(0, "i", score + [self.channel])

	def schedule(self, phase: Phase):
		self.phase.last = (phase.last*self.dur)%1
		self.phase.main = (phase.main*self.dur)%1
		for p in staff.phases:
			# normal crossing
			if self.phase.last < p <= self.phase.main:
				self.send_event()
			# wraparound crossing (phase reset from ~1.0 back to ~0.0)
			elif self.phase.main < self.phase.last and (p > self.phase.last or p <= self.phase.main):
				self.send_event()

origin = 400

# Global staves list with thread lock
staves_lock = threading.Lock()

staves = [
	Staff("tinyosc", euclidean(8, 8), [origin, origin*3/2], 64),
]
""" staves = [
	Staff("tinyosc", euclidean(5, 8), [origin, origin*3/2], 32),
	Staff("tinyosc", euclidean(6, 8), [origin/3, origin/2, origin*5/2], 48),
] """
""" staves = [
	Staff(10, euclidean(8, 8), [origin, origin*3/2], 8),
	Staff(10, euclidean(8, 8), [origin/3, origin/2, origin*5/2], 6),
] """
""" staves = [
	Staff(10, euclidean(5, 8), [origin, origin*3/2], 4),
	Staff(10, euclidean(5, 8), [origin*3/2, origin*3], 4+1/8),
	Staff(10, euclidean(5, 8), [origin*6/5, origin*7/8], 4+1/16),
	Staff(10, euclidean(5, 8), [origin*9/8, origin*4/3], 4+1/24),
] """

# Initialize runtime state
for staff in staves:
	staff.current_talea = staff.talea.copy()
	staff.current_dur = staff.dur
	staff.next_cycle_start = cs.scoreTime()

def add_staff(new_staff):
	"""Add a new staff member"""
	with staves_lock:
		new_staff.current_talea = new_staff.talea.copy()
		new_staff.current_dur = new_staff.dur
		new_staff.next_cycle_start = cs.scoreTime()
		staves.append(new_staff)

def remove_staff(index):
	"""Remove a staff member"""
	with staves_lock:
		if 0 <= index < len(staves):
				del staves[index]

def scheduler_fn():
	phase = Phase()
	while True:
		phase.main, _ = cs.controlChannel("main_phase")

		for staff in staves:
			staff.schedule(phase)
   
		phase.last = phase.main
		time.sleep(QUERY_SLEEP_TIME)
		
# Start scheduler
sched_thread = threading.Thread(target=scheduler_fn, daemon=True)
sched_thread.start()

class LiveCodingREPL(code.InteractiveConsole):
	"""Custom REPL with direct access to staves and live coding environment"""
	
	def __init__(self, locals):
		super().__init__(locals)
		self.locals = locals
	
	def runsource(self, source, filename="<input>", symbol="single"):
		"""Execute code and handle exceptions gracefully"""
		try:
				code = compile(source, filename, symbol)
				# Check if it's a complete statement
				if code is None:
					return True
				
				# Execute in our namespace
				exec(code, self.locals)
				return False
		except SyntaxError as e:
				if e.msg == 'unexpected EOF while parsing':
					return True  # Incomplete
				self.showsyntaxerror(filename)
				return False
		except Exception as e:
				self.showtraceback()
				return False

# Prepare the environment with all your live coding objects
repl_locals = {
	'staves': staves,
	'euclidean': euclidean,
	'Staff': Staff,
	'add_staff': add_staff,
	'remove_staff': remove_staff,
	'cs': cs,
	'pt': pt,
	'threading': threading,
	'time': time,
	# Add any other functions/variables you need
}

print("\n=== Live Coding REPL Active ===")
print("You have direct access to:")
print("  - staves (list of Staff objects)")
print("  - cs (Csound instance)")
print("  - pt (PerformanceThread)")
print("  - euclidean(), update_staff_pattern(), add_staff(), remove_staff()")
print("\nExamples:")
print("  >>> staves[0].colores = [880]")
print("  >>> staves.append(Staff(1, euclidean(5,8), [660], 2.0))")
print("  >>> staves[1].dur = 3.0")
print("  >>> staves[0].talea = euclidean(7,12)")
print("  >>> print(f'Active voices: {len(staves)}')")
print("\nType Ctrl+D or 'exit()' to quit\n")

# Start the REPL
repl = LiveCodingREPL(repl_locals)
repl.interact(banner="")
# Cleanup after REPL exits
print("\nStopping performance...")

# Clean shutdown
pt.stop()
pt.join()
cs.stop()