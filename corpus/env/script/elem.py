import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.interpolate import interp1d
import os
import struct
from mendeleev import element
import warnings
warnings.filterwarnings('ignore')

# Create output directories
os.makedirs('el_files', exist_ok=True)

# Number of samples
N_SAMPLES = 8192
SAMPLE_RATE = 48000

def get_property_safely(elem, prop_name, default=0.0):
	"""Safely get element property with fallback"""
	try:
		if hasattr(elem, prop_name):
				val = getattr(elem, prop_name)
				return float(val) if val is not None else default
	except:
		pass
	return default

def create_wave_terrain(atomic_num, num_peaks, complexity):
	"""Generate a wave terrain-inspired envelope with multiple peaks and valleys"""
	x = np.linspace(0, 1, N_SAMPLES)
	
	# Generate base terrain using multiple sine waves of different frequencies
	terrain = np.zeros(N_SAMPLES)
	for i in range(1, num_peaks + 1):
		freq = atomic_num * i / 20.0
		phase = np.sin(atomic_num * i * 0.1) * np.pi
		terrain += np.sin(freq * x * np.pi + phase) / i
	
	# Create complexity through frequency modulation
	mod = np.sin(complexity * x * np.pi)
	terrain = terrain * (0.5 + 0.5 * mod)
	
	# Force start and end to zero
	fade_length = N_SAMPLES // 16
	fade_in = np.linspace(0, 1, fade_length)
	fade_out = np.linspace(1, 0, fade_length)
	terrain[:fade_length] *= fade_in
	terrain[-fade_length:] *= fade_out
	
	# Normalize to ensure peak is exactly 1.0
	terrain = np.abs(terrain)
	terrain = terrain / np.max(terrain)
	
	# Invert some sections for variety based on atomic number
	if atomic_num % 3 == 0:
		terrain = 1 - terrain
	
	return terrain

def create_cellular_automaton(atomic_num, rule=30):
	"""Generate envelope based on 1D cellular automaton patterns"""
	# Use element properties to seed the automaton
	seed = atomic_num * 12345
	np.random.seed(seed)
	
	# Generate automaton history
	rows = 64
	cols = 128
	history = np.zeros((rows, cols))
	history[0] = np.random.choice([0, 1], cols, p=[0.7, 0.3])
	
	# Apply cellular automaton rules
	for i in range(1, rows):
		for j in range(cols):
				left = history[i-1, (j-1) % cols]
				center = history[i-1, j]
				right = history[i-1, (j+1) % cols]
				pattern = (left, center, right)
				
				# Modified rule based on atomic number
				rule_num = (rule + atomic_num) % 256
				if pattern == (0, 0, 0): history[i, j] = (rule_num >> 0) & 1
				elif pattern == (0, 0, 1): history[i, j] = (rule_num >> 1) & 1
				elif pattern == (0, 1, 0): history[i, j] = (rule_num >> 2) & 1
				elif pattern == (0, 1, 1): history[i, j] = (rule_num >> 3) & 1
				elif pattern == (1, 0, 0): history[i, j] = (rule_num >> 4) & 1
				elif pattern == (1, 0, 1): history[i, j] = (rule_num >> 5) & 1
				elif pattern == (1, 1, 0): history[i, j] = (rule_num >> 6) & 1
				elif pattern == (1, 1, 1): history[i, j] = (rule_num >> 7) & 1
	
	# Sum across columns with different weights per row
	weights = np.linspace(1, 0.5, rows)
	raw = np.sum(history * weights[:, np.newaxis], axis=1)
	
	# Interpolate to 8192 samples
	x_old = np.linspace(0, 1, len(raw))
	x_new = np.linspace(0, 1, N_SAMPLES)
	interpolator = interp1d(x_old, raw, kind='cubic')
	envelope = interpolator(x_new)
	
	# Smooth and normalize
	window_size = 128
	window = np.hanning(window_size)
	envelope = signal.convolve(envelope, window, mode='same') / sum(window)
	
	# Force start and end to zero
	envelope = envelope - np.min(envelope)
	fade_len = N_SAMPLES // 8
	envelope[:fade_len] *= np.linspace(0, 1, fade_len)
	envelope[-fade_len:] *= np.linspace(1, 0, fade_len)
	
	# Normalize to [0, 1] with peak at 1.0
	envelope = envelope / np.max(envelope)
	
	return envelope

def create_fractal_landscape(atomic_num, iterations=5):
	"""Generate envelope using fractal noise (like a 1D landscape)"""
	np.random.seed(atomic_num * 42)
	
	# Start with random points
	n_points = 2 ** iterations + 1
	points = np.random.rand(n_points) * 0.5
	
	# Apply midpoint displacement
	step = n_points - 1
	scale = 1.0
	
	while step > 1:
		half_step = step // 2
		for i in range(0, n_points - 1, step):
				midpoint = i + half_step
				# Calculate average of neighbors plus random displacement
				points[midpoint] = (points[i] + points[i + step]) / 2 + np.random.randn() * scale * 0.5
		step = half_step
		scale *= 0.5 ** (1.0 / (atomic_num / 20.0 + 0.5))
	
	# Interpolate to 8192 samples
	x_old = np.linspace(0, 1, n_points)
	x_new = np.linspace(0, 1, N_SAMPLES)
	interpolator = interp1d(x_old, points, kind='cubic')
	envelope = interpolator(x_new)
	
	# Create organic valleys and peaks
	# Add resonant peaks based on atomic number
	resonance_points = max(1, atomic_num // 10)
	for i in range(resonance_points):
		pos = (i + 1) / (resonance_points + 1)
		width = 0.05 + np.random.rand() * 0.1
		gaussian = np.exp(-((x_new - pos) ** 2) / (2 * width ** 2))
		envelope += gaussian * 0.3 * (i + 1)
	
	# Force start and end to zero with smooth curves
	fade_length = N_SAMPLES // 20
	envelope[:fade_length] *= (np.sin(np.linspace(0, np.pi/2, fade_length))) ** 2
	envelope[-fade_length:] *= (np.cos(np.linspace(0, np.pi/2, fade_length))) ** 2
	
	# Ensure no negative values
	envelope = envelope - np.min(envelope)
	
	# Normalize to [0, 1] with peak at exactly 1.0
	envelope = envelope / np.max(envelope)
	
	# Apply subtle modulation for texture
	texture = 1 + 0.1 * np.sin(atomic_num * 10 * x_new * np.pi)
	envelope = envelope * texture
	
	# Re-normalize
	envelope = envelope / np.max(envelope)
	
	return envelope

def create_orbital_pattern(atomic_num):
	"""Generate envelope based on electron orbital filling patterns"""
	# Simulate electron orbital filling order
	orbitals = ['1s', '2s', '2p', '3s', '3p', '4s', '3d', '4p', '5s', '4d', '5p', '6s', '4f', '5d', '6p', '7s', '5f', '6d', '7p']
	n_electrons = atomic_num
	
	# Calculate orbital occupancy
	orbital_fill = []
	remaining = n_electrons
	for orbital in orbitals:
		max_e = 2 if orbital[1] == 's' else (6 if orbital[1] == 'p' else (10 if orbital[1] == 'd' else 14))
		fill = min(remaining, max_e)
		orbital_fill.append(fill / max_e)
		remaining -= fill
		if remaining <= 0:
				break
	
	# Create envelope based on orbital filling
	x = np.linspace(0, 1, N_SAMPLES)
	envelope = np.zeros(N_SAMPLES)
	
	for i, fill_ratio in enumerate(orbital_fill):
		# Each orbital creates a wave packet
		pos = (i + 0.5) / len(orbital_fill)
		width = 0.05 / len(orbital_fill) + 0.02
		
		# Main orbital peak
		gaussian = np.exp(-((x - pos) ** 2) / (2 * width ** 2))
		
		# Add electron cloud oscillations
		freq = (i + 1) * 10
		oscillation = 1 + 0.3 * np.sin(2 * np.pi * freq * x + np.pi * fill_ratio)
		
		envelope += gaussian * fill_ratio * oscillation
	
	# Force start and end to zero
	fade_len = N_SAMPLES // 10
	envelope[:fade_len] *= np.sin(np.linspace(0, np.pi/2, fade_len)) ** 2
	envelope[-fade_len:] *= np.cos(np.linspace(0, np.pi/2, fade_len)) ** 2
	
	# Ensure minimum at zero
	envelope = envelope - np.min(envelope)
	
	# Normalize to [0, 1]
	envelope = envelope / np.max(envelope)
	
	# Make more dynamic by enhancing peaks
	envelope = envelope ** (0.7 + atomic_num / 200)
	envelope = envelope / np.max(envelope)
	
	return envelope

def create_quantum_bounce(atomic_num, atomic_weight, ionization_energy):
	"""Generate envelope based on quantum-like behavior with bouncing peaks"""
	x = np.linspace(0, 1, N_SAMPLES)
	
	# Number of bounces determined by electron shells
	n_shells = max(1, int(np.ceil(np.log2(atomic_num))))
	n_bounces = min(20, n_shells + 2)
	
	envelope = np.zeros(N_SAMPLES)
	
	# Create bouncing peaks that decay
	bounce_positions = np.linspace(0.05, 0.95, n_bounces) ** 0.8
	bounce_heights = np.exp(-np.arange(n_bounces) * (0.1 + atomic_weight / 1000))
	
	for i, (pos, height) in enumerate(zip(bounce_positions, bounce_heights)):
		# Each bounce is a sharp attack with exponential decay
		idx = int(pos * N_SAMPLES)
		if idx < N_SAMPLES:
				decay = np.exp(-np.arange(N_SAMPLES - idx) * (0.01 + i * 0.05))
				
				# Make first bounce the highest (will be normalized to 1.0)
				if i == 0:
					envelope[idx:] = np.maximum(envelope[idx:], decay * height)
				else:
					envelope[idx:] = np.maximum(envelope[idx:], decay * height * 0.8)
	
	# Add quantum fluctuations between bounces
	fluctuation = 0.05 * np.sin(ionization_energy / 100 * x * np.pi) * np.random.rand(N_SAMPLES) * 0.5
	envelope += fluctuation
	
	# Force start and end to zero
	fade_len = N_SAMPLES // 20
	envelope[:fade_len] *= np.sin(np.linspace(0, np.pi/2, fade_len))
	envelope[-fade_len:] *= np.cos(np.linspace(0, np.pi/2, fade_len))
	
	# Ensure non-negative
	envelope = np.maximum(0, envelope)
	
	# Normalize to [0, 1]
	envelope = envelope / np.max(envelope)
	
	return envelope

def create_spectral_bloom(atomic_num, electronegativity, period):
	"""Create envelope inspired by spectral analysis and blooming patterns"""
	x = np.linspace(0, 1, N_SAMPLES)
	
	# Create spectral bloom pattern
	envelope = np.zeros(N_SAMPLES)
	
	# Number of spectral lines based on period
	n_lines = period * 2
	
	for i in range(n_lines):
		# Line position with slight randomness
		pos = (i + 0.5) / n_lines + np.random.randn() * 0.01
		pos = np.clip(pos, 0, 1)
		
		# Line intensity based on electronegativity pattern
		intensity = 0.3 + 0.7 * np.abs(np.sin(np.pi * i / n_lines + electronegativity))
		
		# Line width varies
		width = 0.01 + 0.03 * (1 - i / n_lines)
		
		# Create blooming effect (Gaussian that widens over time)
		idx_center = int(pos * N_SAMPLES)
		for t in range(N_SAMPLES):
				time_factor = t / N_SAMPLES
				dynamic_width = width * (0.5 + time_factor)
				gauss_val = np.exp(-((t/N_SAMPLES - pos) ** 2) / (2 * dynamic_width ** 2))
				envelope[t] += gauss_val * intensity * (1 - 0.5 * time_factor)
	
	# Add interference pattern
	interference = np.sin(atomic_num * np.pi * x) * 0.3
	envelope += interference
	
	# Force start and end to zero
	fade_len = N_SAMPLES // 15
	envelope[:fade_len] *= np.sin(np.linspace(0, np.pi/2, fade_len)) ** 3
	envelope[-fade_len:] *= np.cos(np.linspace(0, np.pi/2, fade_len)) ** 3
	
	# Ensure non-negative
	envelope = np.maximum(0, envelope)
	
	# Normalize to [0, 1]
	envelope = envelope / np.max(envelope)
	
	return envelope

def create_envelope_for_element(elem):
	"""Choose a creative envelope generation method based on element properties"""
	atomic_number = elem.atomic_number
	atomic_weight = float(elem.atomic_weight) if elem.atomic_weight else atomic_number * 2
	electronegativity = get_property_safely(elem, 'electronegativity_pauling', 0.0)
	ionization_energy = get_property_safely(elem, 'ionization_energy', 100 + atomic_number * 10)
	atomic_radius = get_property_safely(elem, 'atomic_radius', 50 + atomic_number)
	period = elem.period if elem.period else max(1, int(atomic_number / 18) + 1)
	group = elem.group_id if hasattr(elem, 'group_id') and elem.group_id else 1
	
	# Select envelope generation method based on element properties
	methods = []
	
	# Method selection criteria
	if atomic_number <= 18:  # First 3 periods - simpler patterns
		methods.append(('quantum_bounce', create_quantum_bounce(atomic_number, atomic_weight, ionization_energy)))
	elif 19 <= atomic_number <= 54:  # Transition metals - complex patterns
		methods.append(('orbital_pattern', create_orbital_pattern(atomic_number)))
	elif 55 <= atomic_number <= 86:  # Heavy elements - fractal landscapes
		methods.append(('fractal_landscape', create_fractal_landscape(atomic_number, 5)))
	else:  # Super heavy elements - cellular automaton
		methods.append(('cellular_automaton', create_cellular_automaton(atomic_number, rule=atomic_number % 256)))
	
	# Add alternative methods based on other properties
	if electronegativity > 2.0:
		methods.append(('spectral_bloom', create_spectral_bloom(atomic_number, electronegativity, period)))
	if atomic_radius > 150:
		methods.append(('wave_terrain', create_wave_terrain(atomic_number, max(1, period), electronegativity + 1)))
	if ionization_energy > 1000:
		methods.append(('quantum_bounce', create_quantum_bounce(atomic_number, atomic_weight, ionization_energy)))
	
	# Add more variety for specific groups
	if group == 18:  # Noble gases - use spectral bloom
		methods.append(('spectral_bloom', create_spectral_bloom(atomic_number, electronegativity, period)))
	elif group == 1:  # Alkali metals - wave terrain
		methods.append(('wave_terrain', create_wave_terrain(atomic_number, period, 2.0)))
	elif group == 17:  # Halogens - orbital pattern
		methods.append(('orbital_pattern', create_orbital_pattern(atomic_number)))
	
	# Randomly select from available methods (seeded by atomic number for reproducibility)
	np.random.seed(atomic_number * 123)
	selected_method = methods[np.random.randint(len(methods))]
	
	envelope = selected_method[1]
	
	# Ensure envelope is exactly between 0 and 1
	envelope = np.clip(envelope, 0.0, 1.0)
	
	# Force exact start and end to zero
	envelope[0] = 0.0
	envelope[-1] = 0.0
	
	# Ensure at least one sample reaches exactly 1.0
	if np.max(envelope) < 1.0:
		envelope = envelope / np.max(envelope)
	
	# Generate audio by applying envelope to a carrier wave
	# Create carrier based on element properties
	t = np.linspace(0, N_SAMPLES / SAMPLE_RATE, N_SAMPLES, endpoint=False)
	base_freq = 20 + (atomic_number / 118) * 2000
	
	# Create rich timbre
	audio = np.zeros(N_SAMPLES)
	num_harmonics = min(10, period + 1)
	for h in range(1, num_harmonics + 1):
		amplitude = 1.0 / h
		phase = np.random.random() * 2 * np.pi
		audio += amplitude * np.sin(2 * np.pi * base_freq * h * t + phase)
	
	# Apply envelope
	audio = audio / np.max(np.abs(audio)) if np.max(np.abs(audio)) > 0 else audio
	audio = audio * envelope
	
	# Normalize audio
	max_abs = np.max(np.abs(audio))
	if max_abs > 0:
		audio = audio / max_abs
	
	return audio, envelope, base_freq, selected_method[0]

def save_wav(filename, audio_data, sample_rate=SAMPLE_RATE):
	"""Save audio as 32-bit float WAV file"""
	audio_float = audio_data.astype(np.float32)
	
	n_samples = len(audio_float)
	data_size = n_samples * 4
	
	with open(filename, 'wb') as f:
		# RIFF header
		f.write(b'RIFF')
		f.write(struct.pack('<I', 36 + data_size))
		f.write(b'WAVE')
		
		# fmt chunk
		f.write(b'fmt ')
		f.write(struct.pack('<I', 16))
		f.write(struct.pack('<H', 3))  # IEEE float
		f.write(struct.pack('<H', 1))  # Mono
		f.write(struct.pack('<I', sample_rate))
		f.write(struct.pack('<I', sample_rate * 4))
		f.write(struct.pack('<H', 4))
		f.write(struct.pack('<H', 32))
		
		# data chunk
		f.write(b'data')
		f.write(struct.pack('<I', data_size))
		f.write(audio_float.tobytes())

def plot_envelope(envelope, audio, elem, method_name, filename):
	"""Create enhanced visualization of the creative envelope"""
	fig = plt.figure(figsize=(16, 10))
	
	# Create grid for plots
	gs = plt.GridSpec(3, 2, figure=fig, height_ratios=[1, 1, 0.3])
	
	# Time axis
	t = np.linspace(0, N_SAMPLES / SAMPLE_RATE * 1000, N_SAMPLES)
	
	# 1. Envelope plot (spanning full width)
	ax1 = fig.add_subplot(gs[0, :])
	ax1.plot(t, envelope, 'b-', linewidth=1.5, alpha=0.8)
	ax1.fill_between(t, 0, envelope, alpha=0.2, color='blue')
	
	# Highlight where envelope = 1.0
	peaks = np.where(envelope >= 0.99)[0]
	if len(peaks) > 0:
		ax1.scatter(t[peaks[::10]], envelope[peaks[::10]], color='red', s=20, alpha=0.6, label='Peaks')
	
	ax1.set_title(f'{elem.symbol} - {elem.name} (Z={elem.atomic_number}) | Method: {method_name}', 
						fontsize=16, fontweight='bold', color='darkblue')
	ax1.set_xlabel('Time (ms)')
	ax1.set_ylabel('Amplitude')
	ax1.grid(True, alpha=0.3, linestyle='--')
	ax1.set_xlim(0, t[-1])
	ax1.set_ylim(-0.05, 1.1)
	ax1.legend(loc='upper right')
	
	# 2. Audio waveform
	ax2 = fig.add_subplot(gs[1, :])
	ax2.plot(t, audio, 'k-', linewidth=0.3, alpha=0.7)
	ax2.fill_between(t, -1, 1, color='lightgray', alpha=0.1)
	ax2.set_title('Audio Waveform', fontsize=14, color='darkgreen')
	ax2.set_xlabel('Time (ms)')
	ax2.set_ylabel('Amplitude')
	ax2.grid(True, alpha=0.3)
	ax2.set_xlim(0, t[-1])
	ax2.set_ylim(-1.1, 1.1)
	
	# 3. Info panel
	ax3 = fig.add_subplot(gs[2, :])
	ax3.axis('off')
	
	info_text = f'Method: {method_name.replace("_", " ").title()} | '
	info_text += f'Z={atomic_num} | '
	info_text += f'Weight: {elem.atomic_weight:.1f}' if elem.atomic_weight else 'Weight: N/A'
	info_text += f' | Period: {elem.period}' if elem.period else ' | Period: N/A'
	info_text += f' | Group: {elem.group_id}' if hasattr(elem, 'group_id') and elem.group_id else ' | Group: N/A'
	
	ax3.text(0.5, 0.5, info_text, transform=ax3.transAxes, 
				ha='center', va='center', fontsize=10, family='monospace',
				bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
	
	plt.tight_layout()
	plt.savefig(filename, dpi=150, bbox_inches='tight')
	plt.close()

# Main execution
print("🎵 Generating Creative Periodic Table Element Envelopes 🎵")
print("=" * 70)
print(f"Total elements: 118")
print(f"Envelope types: wave_terrain, cellular_automaton, fractal_landscape, orbital_pattern, quantum_bounce, spectral_bloom")
print("=" * 70)

elements_processed = 0
elements_skipped = 0
method_counts = {}

for atomic_num in range(1, 119):
	try:
		elem = element(atomic_num)
		
		# Create safe filename
		safe_symbol = elem.symbol.replace(' ', '_')
		safe_name = elem.name.replace(' ', '_').replace('/', '_')
		#wav_filename = f'el_files/{atomic_num:03d}_{safe_symbol}_{safe_name[3:].lower()}.wav'
		#png_filename = f'el_files/{atomic_num:03d}_{safe_symbol}_{safe_name}.png'
		wav_filename = f'el_files/{safe_name[:3].lower()}.wav'
		png_filename = f'el_files/{safe_name[:3].lower()}.png'
		
		# Generate creative envelope
		audio, envelope, freq, method = create_envelope_for_element(elem)
		
		# Verify constraints
		assert envelope[0] == 0.0, f"Start not zero: {envelope[0]}"
		assert envelope[-1] == 0.0, f"End not zero: {envelope[-1]}"
		assert 1.0 in envelope or np.max(envelope) >= 0.999, f"No peak at 1.0: max={np.max(envelope)}"
		assert np.min(envelope) >= 0.0, f"Below zero: {np.min(envelope)}"
		assert np.max(envelope) <= 1.0, f"Above 1.0: {np.max(envelope)}"
		
		# Save files
		save_wav(wav_filename, audio)
		plot_envelope(envelope, audio, elem, method, png_filename)
		
		elements_processed += 1
		method_counts[method] = method_counts.get(method, 0) + 1
		
		print(f"✓ #{atomic_num:3d}: {elem.symbol:3s} - {elem.name:15s} | "
				f"Method: {method:20s} | Freq: {freq:6.1f} Hz | "
				f"Peaks: {len(np.where(envelope >= 0.99)[0])}")
		
	except Exception as e:
		elements_skipped += 1
		error_msg = f"✗ Error with element {atomic_num}: {str(e)}"
		print(error_msg)

print("=" * 70)
print(f"\n✨ Complete! Processed {elements_processed}/118 elements successfully!")
if elements_skipped > 0:
	print(f"⚠ Skipped {elements_skipped} elements due to errors.")

print(f"\n📁 Output directories:")
print(f"   WAV files: wav_files/")
print(f"   PNG visualizations: png_files/")

print(f"\n🎨 Envelope method distribution:")
for method, count in sorted(method_counts.items()):
	bar = "█" * (count // 2)
	print(f"   {method:25s}: {count:3d} elements {bar}")

print(f"\n🔬 Creative envelope types used:")
print("   • Wave Terrain: Multi-frequency interference patterns")
print("   • Cellular Automaton: Rule-based pattern generation")
print("   • Fractal Landscape: Midpoint displacement terrain")
print("   • Orbital Pattern: Electron shell filling simulation")
print("   • Quantum Bounce: Decaying resonant peaks")
print("   • Spectral Bloom: Dynamic line broadening")
print(f"\n✅ All envelopes: 0→1→0, max=1.0, 8192 samples, 32-bit float WAV")