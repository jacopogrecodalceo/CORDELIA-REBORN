from dataclasses import dataclass

import ctcsound
import time
import threading
import code
import math
import random
import abjad, rmakers

CHANNELs = 2


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

gkpulse init 60
gkdiv init 64
	instr 1
gkpulse = 60;+jitter(50, 1/8, 1)
kphase phasor (gkpulse / gkdiv) / 60
	chnset kphase, "main_phase"
	endin
	alwayson(1)

	instr tiny_osc
idur init p3
icps init p4
irel init idur+random(.005, -.005)
	xtratim irel

anoi fractalnoise 1/12+random(0, .005), 1
aosc oscil3 .5+random(-.005, .005), icps
avco vco2 1/64+random(0, .005), icps

aout sum aosc, anoi*cosseg(1, .005+random(.0095, .005), 0), avco
aout = aout * (.5 + oscil3:a(cossegr:a(0, idur, 1, idur, random(.25, .5), irel, 0)/4, 3+random(-.005, .005)))

aenv cossegr 0, .005, 1, idur - .005, random(1/8, 1/24), irel, 0
aout *= aenv
	outch p5, aout/3
	endin

"""

KSMPS = cs.ksmps()
SR = cs.sr()
QUERY_SLEEP_TIME = 1/12

FTGEN_SIZE = 8192

result = cs.compileOrc(orc)
if result != 0:
	raise ValueError("ERROR in compiling the orchestra")

cs.start()

pt = ctcsound.CsoundPerformanceThread(cs.csound())
pt.play()
time.sleep(1/4)

# all talea's opcode need to send a series of 1s and 0s
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


def make_a_talea(counts: list = [1, 2, 3, 4]):
	
	talea = []
	tuplets = rmakers.make_talea_tuplets(abjad.Duration((4, 4)), counts, 16)
	rmakers.extract_trivial_tuplets(tuplets)
	staff = abjad.Staff(tuplets)
	ties = abjad.select.logical_ties(staff, pitched=True)
	for i, tie in enumerate(ties):
		first_note = tie[0]
		time_span = abjad.get.timespan(first_note)		
		onset = time_span.start_offset

		x = math.floor(FTGEN_SIZE*onset)
		y = i
		talea.append(1)



def talea_to_ftgen(talea: list, size: float = 8192) -> list:
	talea_len = len(talea)
	min_segment = size // talea_len
	ftgen = []

	count = 1
	for i, n in enumerate(talea):
		if n > 0:
			x = min_segment*i
			if n == 1:
				y = count
				count += 1
			else:
				y = n
		else:
			x = min_segment*i
			y = 0
		ftgen.append(x)
		ftgen.append(y)
	return ftgen

# ---

@dataclass
class Phase:
	main: float = 0
	last: float = 0


MAIN_DIRTY = False
MAIN_SCORE = []

class Staff:
	_ftgen_counter = 101  # Class variable

	def __init__(self, instrument, talea, colores, dur):
		# main parameters
		self.instrument = instrument
		self.talea = talea  
		self.colores = colores
		self.dur = dur
		self._colores_count = 0
		self.dirty = False
		self.born = True
		self.channel = 0

		self.make_ftgen_num()

	def make_ftgen_num(self):
		self.talea_ftgen_num = Staff._ftgen_counter
		Staff._ftgen_counter += 1
		self.colores_ftgen_num = Staff._ftgen_counter
		Staff._ftgen_counter += 1
    
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
		for p in self.phases:
			# normal crossing
			if self.phase.last < p <= self.phase.main:
				self.send_event()
			# wraparound crossing (phase reset from ~1.0 back to ~0.0)
			elif self.phase.main < self.phase.last and (p > self.phase.last or p <= self.phase.main):
				self.send_event()

	def make_ftgen(self):
		unique_id = f'i{id(self)}'
		talea_ftgen = talea_to_ftgen(self.talea)

		score = [f'; CORDELIA INSTR {unique_id} SCORE BEGIN']

		if self.born:
			score += [f"""
				
gk{unique_id}_dur init {self.dur}
gi{unique_id}_talea ftgen {self.talea_ftgen_num}, 0, {FTGEN_SIZE}, -17, {", ".join(map(str, talea_ftgen))}
gi{unique_id}_colores ftgen {self.colores_ftgen_num}, 0, {FTGEN_SIZE}, -2, {len(self.colores)}, {", ".join(map(str, self.colores))}
gk{unique_id}_colores_count init -1
				
	instr {unique_id}
; INIT ---
ktalea_last init -1
kcolores_flag init 1
kmain chnget "main_phase"
kphase = (kmain*gk{unique_id}_dur)%1
ktalea table kphase, gi{unique_id}_talea, 1

if ktalea > 0 && ktalea != ktalea_last then

	if kcolores_flag == 1 then
		gk{unique_id}_colores_count = ktalea-1
		kcolores_flag = 0
	endif

	kcolores_len table 0, gi{unique_id}_colores
	kcolores_indx = (gk{unique_id}_colores_count%kcolores_len)+1
	kcolores table kcolores_indx, gi{unique_id}_colores

	schedulek "{self.instrument}", 0, 1/12, kcolores, 1
	schedulek "{self.instrument}", 0, 1/12, kcolores, 2

	gk{unique_id}_colores_count += 1
	ktalea_last = ktalea
endif

	endin
	schedule "{unique_id}", ksmps/sr, -1
	"""]
			score += [f'; CORDELIA INSTR {unique_id} SCORE END']
			self.born = False
   
		else:
			score += [f'gk{unique_id}_dur init {self.dur}']
	
			score += [f'gi{unique_id}_talea ftgen {self.talea_ftgen_num}, 0, {FTGEN_SIZE}, -17, {", ".join(map(str, talea_ftgen))}']
			score += [f'gi{unique_id}_colores ftgen {self.colores_ftgen_num}, 0, {FTGEN_SIZE}, -2, {len(self.colores)}, {", ".join(map(str, self.colores))}']
			score += [f'; CORDELIA INSTR {unique_id} SCORE END']
			
		MAIN_SCORE.extend(score)

		self.dirty = False

origin = 400

# Global staves list with thread lock
staves_lock = threading.Lock()

staves = [
	Staff("tiny_osc", euclidean(8, 8), [origin/3, origin*3/2], 32),
	Staff("tiny_osc", euclidean(6, 8), [origin, origin*2], 24),
	Staff("tiny_osc", [1, 0, 0, 1, 1, 0], [500, 750], 16),
	Staff("tiny_osc", euclidean(5, 8), [90]*8 + [150]*12, 64),
	#Staff("tiny_osc", [1, 1, 1, 1] + [0]*4, [origin]*8 + [origin/2]*8, 32),
]
""" staves = [
	Staff("tiny_osc", euclidean(5, 8), [origin, origin*3/2], 32),
	Staff("tiny_osc", euclidean(6, 8), [origin/3, origin/2, origin*5/2], 48),
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



def scheduler_fn():
	global MAIN_SCORE, MAIN_DIRTY   
	while True:
		for staff in staves:
			if staff.dirty or staff.born:
				print('DIRTY STAFF')
				staff.make_ftgen()
				MAIN_DIRTY = True
		if MAIN_DIRTY:
			score = '\n'.join(MAIN_SCORE)
			print(score)
			cs.compileOrcAsync(score)
			MAIN_SCORE = []
			MAIN_DIRTY = False
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