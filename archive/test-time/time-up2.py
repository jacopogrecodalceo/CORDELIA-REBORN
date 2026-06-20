import ctcsound
import time
import threading
import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any

cs = ctcsound.Csound()
cs.setOption("-odac")
cs.setOption("-d")

# Dynamic Csound orchestra that will be updated as we add instruments
ORCHESTRA_TEMPLATE = """
sr     = 48000
ksmps  = 32
nchnls = 2
0dbfs  = 1

; Global reverb send
gk_reverb_send init 0

{instruments}

; Global reverb
instr 99
    aL, aR reverb2 gk_reverb_send, 0.8, 10000
    out aL, aR
endin
"""

INSTRUMENT_TEMPLATE = """
instr {num}
    ; Parameters
    ipitch = p4
    iamp = p5
    iattack = p6
    idecay = p7
    ipan = p8
    ireverb = p9
    
    ; Envelope
    kenv linsegr 0, iattack, 1, idecay, 0
    
    ; Oscillator (with waveform selection)
    kwave = {waveform}
    if kwave == 1 then
        aout oscili iamp * kenv, ipitch
    elseif kwave == 2 then
        aout vco2 iamp * kenv, ipitch
    elseif kwave == 3 then
        aout buzz iamp * kenv, ipitch, {harmonics}
    else
        aout oscili iamp * kenv, ipitch
    endif
    
    ; Panning
    aL = aout * sqrt(1 - ipan)
    aR = aout * sqrt(ipan)
    
    ; Reverb send
    gk_reverb_send = gk_reverb_send + (aout * ireverb)
    
    out aL, aR
endin
"""

class Staff:
    """A musical voice that can generate complex rhythms and parameters"""
    
    def __init__(self, 
                 name: str,
                 rhythm: List[int],  # talea - binary pattern
                 pitches: List[float],  # colores - pitch classes
                 dynamics: List[float] = None,  # dyn - amplitude (0-1)
                 duration: float = 2.0,  # cycle duration in seconds
                 envelope: Tuple[float, float] = (0.005, 0.1),  # attack, decay
                 space: Tuple[float, float] = (0.0, 1.0),  # pan left/right
                 reverb: float = 0.0,  # reverb send amount
                 waveform: int = 1,  # 1=sine, 2=vco, 3=buzz
                 harmonics: int = 10):  # for buzz waveform
        self.name = name
        self.rhythm = rhythm  # talea
        self.pitches = pitches  # colores
        self.dynamics = dynamics or [0.5]  # dyn
        self.cycle_duration = duration  # dur
        self.envelope = envelope  # attack, decay
        self.space = space  # pan range
        self.reverb = reverb
        self.waveform = waveform
        self.harmonics = harmonics
        
        # Auto-generate instrument number
        self.instrument_num = None
        
        # Runtime state
        self.next_cycle_start = 0.0
        self.current_rhythm = rhythm.copy()
        self.current_duration = duration
        self.needs_update = False
        
        # Interpolation state for smooth parameter changes
        self.target_pitches = pitches.copy()
        self.target_dynamics = dynamics or [0.5]
        self.pitch_interp_step = 0
        self.dyn_interp_step = 0
    
    def generate_csound_instrument(self, num: int) -> str:
        """Generate Csound instrument code for this staff"""
        self.instrument_num = num
        return INSTRUMENT_TEMPLATE.format(
            num=num,
            waveform=self.waveform,
            harmonics=self.harmonics
        )
    
    def get_pattern_duration(self) -> float:
        """Calculate duration of one pattern cycle"""
        return self.cycle_duration
    
    def get_step_duration(self) -> float:
        """Calculate duration of each step in the rhythm"""
        return self.cycle_duration / len(self.rhythm)
    
    def get_next_event(self, cycle_start: float, step_index: int) -> Optional[Tuple[float, float, float, float]]:
        """Get the next event (time, duration, pitch, amplitude)"""
        if not self.rhythm[step_index]:
            return None
        
        # Calculate note timing
        step_dur = self.get_step_duration()
        note_time = cycle_start + (step_index * step_dur)
        note_dur = step_dur * 0.95  # Slight gap between notes
        
        # Get pitch (cycle through list)
        pitch = self.pitches[step_index % len(self.pitches)]
        
        # Get dynamics (cycle through list)
        amp = self.dynamics[step_index % len(self.dynamics)]
        
        # Interpolate pan based on position in cycle
        pan_pos = step_index / len(self.rhythm)
        pan = self.space[0] + (self.space[1] - self.space[0]) * pan_pos
        
        # Envelope
        attack, decay = self.envelope
        
        return (note_time, note_dur, pitch, amp, attack, decay, pan, self.reverb)
    
    def update_rhythm(self, new_rhythm: List[int], smooth: bool = True):
        """Update the rhythm pattern"""
        if smooth:
            self.needs_update = True
        self.rhythm = new_rhythm
    
    def update_pitches(self, new_pitches: List[float], smooth: bool = True):
        """Update pitches with optional smoothing"""
        if smooth:
            self.target_pitches = new_pitches
            self.pitch_interp_step = 0
        else:
            self.pitches = new_pitches
    
    def update_dynamics(self, new_dynamics: List[float], smooth: bool = True):
        """Update dynamics with optional smoothing"""
        if smooth:
            self.target_dynamics = new_dynamics
            self.dyn_interp_step = 0
        else:
            self.dynamics = new_dynamics
    
    def interpolate_pitches(self):
        """Smoothly interpolate between current and target pitches"""
        if self.pitch_interp_step < 32:  # Interpolate over 32 steps
            self.pitch_interp_step += 1
            factor = self.pitch_interp_step / 32
            self.pitches = [
                old + (target - old) * factor 
                for old, target in zip(self.pitches, self.target_pitches)
            ]
            return True
        return False
    
    def __repr__(self):
        return f"Staff('{self.name}', rhythm={self.rhythm}, pitches={self.pitches})"


class LiveCodingEngine:
    """Main engine for live coding performance"""
    
    def __init__(self):
        self.cs = ctcsound.Csound()
        self.staves: List[Staff] = []
        self.staves_lock = threading.Lock()
        self.performance_thread = None
        self.scheduler_thread = None
        self.running = False
        
        # Instrument counter
        self.next_instrument = 1
        
    def add_staff(self, staff: Staff):
        """Add a staff to the performance"""
        with self.staves_lock:
            # Generate instrument code
            instr_code = staff.generate_csound_instrument(self.next_instrument)
            self.next_instrument += 1
            
            # Recompile orchestra with new instrument
            self._recompile_orchestra()
            
            # Initialize runtime state
            staff.next_cycle_start = self.cs.scoreTime()
            staff.current_rhythm = staff.rhythm.copy()
            staff.current_duration = staff.cycle_duration
            
            self.staves.append(staff)
            print(f"Added staff: {staff.name}")
    
    def remove_staff(self, index: int):
        """Remove a staff by index"""
        with self.staves_lock:
            if 0 <= index < len(self.staves):
                removed = self.staves.pop(index)
                self._recompile_orchestra()
                print(f"Removed staff: {removed.name}")
    
    def _recompile_orchestra(self):
        """Recompile Csound orchestra with current instruments"""
        # Build instruments string
        instruments = []
        for staff in self.staves:
            if staff.instrument_num:
                instr_code = staff.generate_csound_instrument(staff.instrument_num)
                instruments.append(instr_code)
        
        orchestra = ORCHESTRA_TEMPLATE.format(
            instruments="\n".join(instruments)
        )
        
        # Recompile (this will restart Csound)
        self.cs.compileOrc(orchestra)
    
    def start(self):
        """Start the live coding engine"""
        # Initialize Csound
        self.cs.setOption("-odac")
        self.cs.setOption("-d")
        
        # Start with empty orchestra
        self.cs.compileOrc(ORCHESTRA_TEMPLATE.format(instruments=""))
        self.cs.start()
        
        # Create performance thread
        self.performance_thread = ctcsound.CsoundPerformanceThread(self.cs.csound())
        self.performance_thread.play()
        
        time.sleep(0.125)
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
    
    def _scheduler_loop(self):
        """Main scheduling loop"""
        while self.running:
            now_cs = self.cs.scoreTime()
            
            with self.staves_lock:
                current_staves = self.staves.copy()
            
            for staff in current_staves:
                # Handle updates at cycle boundaries
                if staff.needs_update and staff.next_cycle_start <= now_cs:
                    staff.current_rhythm = staff.rhythm.copy()
                    staff.current_duration = staff.cycle_duration
                    staff.needs_update = False
                    print(f"Staff '{staff.name}' updated at cycle {staff.next_cycle_start:.3f}")
                
                # Handle pitch interpolation
                if staff.pitch_interp_step > 0:
                    if not staff.interpolate_pitches():
                        staff.pitch_interp_step = 0
                
                # Schedule upcoming cycles
                while staff.next_cycle_start <= now_cs + 0.5:
                    step_dur = staff.current_duration / len(staff.current_rhythm)
                    
                    for i, hit in enumerate(staff.current_rhythm):
                        event = staff.get_next_event(staff.next_cycle_start, i)
                        if event:
                            note_time, note_dur, pitch, amp, attack, decay, pan, reverb = event
                            self.performance_thread.scoreEvent(
                                0, "i",
                                (staff.instrument_num, note_time, note_dur, 
                                 pitch, amp, attack, decay, pan, reverb)
                            )
                    
                    staff.next_cycle_start += staff.current_duration
            
            time.sleep(0.01)
    
    def stop(self):
        """Stop the engine"""
        self.running = False
        if self.performance_thread:
            self.performance_thread.stop()
            self.performance_thread.join()
        self.cs.stop()
    
    # Live coding commands
    def rhythm(self, staff_name: str, pulses: int, steps: int):
        """Change rhythm pattern using Euclidean algorithm"""
        new_rhythm = self._euclidean(pulses, steps)
        for staff in self.staves:
            if staff.name == staff_name:
                staff.update_rhythm(new_rhythm)
                print(f"✓ {staff_name}: rhythm → {pulses}/{steps}")
    
    def pitch(self, staff_name: str, *pitches: float):
        """Change pitches"""
        for staff in self.staves:
            if staff.name == staff_name:
                staff.update_pitches(list(pitches), smooth=True)
                print(f"✓ {staff_name}: pitches → {pitches}")
    
    def amp(self, staff_name: str, *amps: float):
        """Change amplitudes"""
        for staff in self.staves:
            if staff.name == staff_name:
                staff.update_dynamics(list(amps), smooth=True)
                print(f"✓ {staff_name}: amplitudes → {amps}")
    
    def tempo(self, staff_name: str, duration: float):
        """Change cycle duration (tempo)"""
        for staff in self.staves:
            if staff.name == staff_name:
                staff.cycle_duration = duration
                staff.needs_update = True
                print(f"✓ {staff_name}: duration → {duration}s")
    
    def reverb(self, staff_name: str, amount: float):
        """Change reverb amount"""
        for staff in self.staves:
            if staff.name == staff_name:
                staff.reverb = amount
                print(f"✓ {staff_name}: reverb → {amount}")
    
    @staticmethod
    def _euclidean(pulses: int, steps: int) -> List[int]:
        """Generate Euclidean rhythm pattern"""
        pattern = []
        bucket = 0
        for _ in range(steps):
            bucket += pulses
            if bucket >= steps:
                bucket -= steps
                pattern.append(1)
            else:
                pattern.append(0)
        return pattern


# Example usage
if __name__ == "__main__":
    engine = LiveCodingEngine()
    engine.start()
    
    # Create some staves
    engine.add_staff(Staff(
        name="kick",
        rhythm=engine._euclidean(3, 8),
        pitches=[60],
        dynamics=[0.8],
        duration=2.0,
        envelope=(0.001, 0.05),
        space=(0.3, 0.7),
        waveform=3,  # buzz for kick
        harmonics=8
    ))
    
    engine.add_staff(Staff(
        name="snare",
        rhythm=engine._euclidean(4, 16),
        pitches=[67, 69],
        dynamics=[0.5, 0.6],
        duration=2.0,
        envelope=(0.002, 0.1),
        space=(0.4, 0.6),
        waveform=2  # vco for snare
    ))
    
    engine.add_staff(Staff(
        name="hat",
        rhythm=engine._euclidean(7, 16),
        pitches=[72, 74, 76],
        dynamics=[0.3],
        duration=1.0,
        envelope=(0.0005, 0.03),
        space=(0.2, 0.8),
        reverb=0.3
    ))
    
    print("\n=== Live Coding Ready ===")
    print("\nCommands (in Python console):")
    print("  engine.rhythm('kick', 5, 8)     # Change kick rhythm")
    print("  engine.pitch('snare', 67, 70)   # Change snare pitches")
    print("  engine.amp('hat', 0.2, 0.4)     # Change hat amplitudes")
    print("  engine.tempo('kick', 3.0)       # Change kick tempo")
    print("  engine.reverb('snare', 0.5)     # Add reverb to snare")
    print("  engine.add_staff(Staff(...))    # Add new instrument")
    print("  engine.remove_staff(0)          # Remove instrument")
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
        engine.stop()