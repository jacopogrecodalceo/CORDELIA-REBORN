from dataclasses import dataclass
import random

import ctcsound
import time
import threading
import code

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

gkbeats		init 1 / (i(gkpulse) / 60)
gkdiv init 64
	instr 1
	prints "HEART is PUMPING"
gkpulse = 60;+jitter(5, 1/8, 1)
kphase phasor (gkpulse / gkdiv) / 60
	chnset kphase, "main_phase"
	endin
	alwayson(1)

	instr tiny_osc
idur init p3
idyn init p4
ienv init p5
icps init p6
ich init p7
irel init idur+random(.005, -.005)
	xtratim irel

anoi fractalnoise 1/12+random(0, .005), 1
aosc oscil3 .5+random(-.005, .005), icps
avco vco2 1/64+random(0, .005), icps

aout sum aosc, anoi*cosseg(1, .005+random(.0095, .005), 0), avco
aout = aout * (.5 + oscil3:a(cossegr:a(0, idur, 1, idur, random(.25, .5), irel, 0)/4, 3+random(-.005, .005)))

aenv cossegr 0, .005, 1, idur - .005, random(1/8, 1/24), irel, 0
aenv_indx linsegr 1, idur, random(1/8, 1/24), irel, 0
;aenv table3 aenv_indx, ienv, 1
aout *= aenv
	outch ich, aout/2*idyn
	endin

"""

orc += """
gienvdur init 8192

;	MIRROR
;	a palindrome 3(6)-points function from linear segments
gimirror_int		init 9
;-----------------------
gimirror_intatk		init .5
gimirror_intdec		init 1
gimirror_intrel		init 3
;-----------------------
gimirror_atk		init gimirror_intatk / gimirror_int
gimirror_dec		init gimirror_intdec / gimirror_int
gimirror_sus		init .35
gimirror_rel		init gimirror_intrel / gimirror_int
;-----------------------
gimirror		ftgen	0, 0, gienvdur, 7, 0, gienvdur*gimirror_atk, 1, gienvdur*gimirror_dec, gimirror_sus, gienvdur*gimirror_rel, 0, gienvdur*gimirror_rel, gimirror_sus, gienvdur*gimirror_dec, 1, gienvdur*gimirror_atk, 0
;-----------------------



giexpzero init .005

;	ECLASSIC
;	a 3-points function from segments of exponential curves
gieclassic_atk		init 30
gieclassic_dur		init gienvdur - gieclassic_atk
gieclassic_int		init 9
gieclassic_intdec	init 5
gieclassic_dec		init gieclassic_intdec / gieclassic_int
gieclassic_sus		init .15
gieclassic_intrel	init gieclassic_int-gieclassic_intdec
gieclassic_rel		init gieclassic_intrel / gieclassic_int
;-----------------------
gieclassic		ftgen	0, 0, gienvdur, 5, giexpzero, gieclassic_atk, 1, gieclassic_dur*gieclassic_dec, gieclassic_sus, gieclassic_dur*gieclassic_rel, giexpzero
;-----------------------

	opcode cordelia_lpf1, a, akk
	ain, kfreq, kq xin

kfreq_var   = (kfreq*11/10)-kfreq
kfreq       = kfreq + jitter(1, 1/8, 1)*kfreq_var

; safe limit
kfreq       limit kfreq, 17.5, 19500

; core
aout        diode_ladder ain, kfreq, 5+kq*10

kdyn_comp   pow (kfreq / sr/2), -0.15
aout        *= kdyn_comp

	xout aout
	endop

"""

KSMPS = cs.ksmps()
SR = cs.sr()
QUERY_SLEEP_TIME = 1/12 #the sleep time in the main while loop

FTGEN_SIZE = 4096 #the size of the ft of qualities

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

def saf(pat: str) -> list[int]:
	table = {"-": [1, 0], "u": [1], ".": [0]}
	result = []
	for ch in pat:
		result.extend(table.get(ch, []))
	return result

MAIN_DIRTY = False
MAIN_SCORE = []

@dataclass
class Quality:
	instrument: str
	talea: list
	colores: list
	space: list
	dur: list
	dyn: list
	env: list
	freq: list

class FtgenRegistry:
	_counter = 1001
	_free = []

	@classmethod
	def alloc(cls) -> int:
		if cls._free:
				return cls._free.pop()
		n = cls._counter
		cls._counter += 1
		return n

	@classmethod
	def free(cls, n: int):
		cls._free.append(n)

class Staff:
	_ftgen_counter = 1001  # Class variable

	def __init__(self, instrument, talea, colores, staff_dur, dur=None, dyn=None, env=None, space=None):
		self.instrument = instrument
		self._talea = talea  
		self.colores = colores
		self.staff_dur = staff_dur
		self.instr_id = f'i{id(self)}'

		self.dirty = False
		self.born = True
		self.channel = 0
		self.params = ['talea', 'colores', 'dur', 'dyn', 'env', 'space']

		if not dur:

			result = []
			count = 1
			for x in reversed(self.talea):
				if x == 0:
					count += 1
				else:
					result.append(count)
					count = 1
			self.dur = list(reversed(result))
     
		else:
			self.dur = dur

		if not dyn:
			self.dyn = [1] + [1/2]*(len(self.dur)-1)
		else:
			self.dyn = dyn

		if not env:
			self.env = ['gieclassic', 'gieclassic']
		else:
			self.env = env

		if not space:
			self.space = [0]
		else:
			self.space = space

		self.make_ft_nums()

	def make_ft_nums(self):
		for p in self.params:
			setattr(self, f'{p}_ft_num', Staff._ftgen_counter)
			Staff._ftgen_counter += 1

	def update(self, **kwargs):
		for key, value in kwargs.items():
			if hasattr(self, key):
				setattr(self, key, value)
				self.dirty = True

	@property
	def talea(self):
		result = []
		count = 1
		for x in self._talea:
			if x == 1:
				result.append(count)
				count += 1
			else:
				result.append(0)
		return result

	def make(self):
		score = []
		
		# === Helper functions ===
		def param_lines(param_name):
			"""Generate ftgen and table lines for a parameter"""
			values = getattr(self, param_name)
			ft_num = getattr(self, f'{param_name}_ft_num')
			
			ftgen = f'gi{self.instr_id}_{param_name} ftgen {ft_num}, 0, {FTGEN_SIZE}, -2, {len(values)}, {", ".join(map(str, values))}'
			
			table = f"""
k{param_name}_len table 0, gi{self.instr_id}_{param_name}
k{param_name}_idx = (gk{self.instr_id}_{param_name}_count % k{param_name}_len) + 1
k{param_name} table k{param_name}_idx, gi{self.instr_id}_{param_name}"""
			
			return ftgen, table
		
		# === Generate all parameter lines ===
		ftgens = []
		tables = []
		count_vars = []
		
		for p in self.params:
			if p != 'talea':
					ftgen, table = param_lines(p)
					ftgens.append(ftgen)
					tables.append(table)
					count_vars.append(f'gk{self.instr_id}_{p}_count')
		
		# === Build the instrument ===
		instr_template = f"""
	; --- Staff {self.instr_id} ---
	gk{self.instr_id}_dur init {self.staff_dur}
	gi{self.instr_id}_talea ftgen {self.talea_ft_num}, 0, {FTGEN_SIZE}, -2, {len(self.talea)}, {", ".join(map(str, self.talea))}

	{chr(10).join(ftgens)}
	{chr(10).join([f'{v} init -1' for v in count_vars])}

	instr {self.instr_id}
		ktalea_last init -1
		kinit_flag init 1
		
		kmain chnget "main_phase"
		kphase = (kmain * gk{self.instr_id}_dur) % 1
		ktalea_len = {len(self.talea)}
		ktalea_idx = int(kphase * ktalea_len) + 1
		ktalea table ktalea_idx, gi{self.instr_id}_talea
		
		if ktalea > 0 && ktalea != ktalea_last then
			if kinit_flag == 1 then
					{chr(10).join([f'{v} = ktalea - 1' for v in count_vars])}
					kinit_flag = 0
			endif
			
			{chr(10).join(tables)}
			
			; Schedule events
			if kspace == 0 then
					kch = 1
					until kch > nchnls do
						schedulek "{self.instrument}", 0, kdur * gkbeats * gk{self.instr_id}_dur / gkdiv, kdyn, kenv, kcolores, kch
						kch += 1
					od
			else
					schedulek "{self.instrument}", 0, kdur * gkbeats * gk{self.instr_id}_dur / gkdiv, kdyn, kenv, kcolores, kspace
			endif
			
			{chr(10).join([f'{v} += 1' for v in count_vars])}
			ktalea_last = ktalea
		endif
	endin

	schedule "{self.instr_id}", ksmps/sr, -1
	"""
		
		# === Add to score ===
		if self.born:
			score.append(f'; CORDELIA INSTR {self.instr_id} BORN')
			score.append(instr_template)
			self.born = False
		else:
			score.append(f'; CORDELIA INSTR {self.instr_id} UPDATE')
			score.append(f'gk{self.instr_id}_dur init {self.staff_dur}')
			score.extend(ftgens)
		
		MAIN_SCORE.extend(score)
		self.dirty = False
  
origin = 400

# Global staves list with thread lock
staves_lock = threading.Lock()

staves = [
	Staff("tiny_osc", euclidean(3, 8), [origin/3, origin*3/2], 32),
	Staff("tiny_osc", saf('-u-u.'), [origin/3, origin*3/2], 32),
#	Staff("tiny_osc", [1, 0, 0, 1] + [0]*4, [origin]*2 + [origin/2]*2, 24),
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
	Staff("tiny_osc", euclidean(5, 8), [origin, origin*3/2], 4),
	Staff("tiny_osc", euclidean(5, 8), [origin*3/2, origin*3], 4+1/8),
	Staff("tiny_osc", euclidean(5, 8), [origin*6/5, origin*7/8], 4+1/16),
	Staff("tiny_osc", euclidean(5, 8), [origin*9/8, origin*4/3], 4+1/24),
] """

""" for i in range(8):
	staves += [Staff("tiny_osc", [1, 0, 1, 1], [random.randint(12, 120)*10]*random.randint(2, 5), random.randint(2, 12))] """

def scheduler_fn():
	global MAIN_SCORE, MAIN_DIRTY   
	while True:
		for staff in staves:
			if staff.dirty or staff.born:
				print('DIRTY STAFF')
				staff.make()
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