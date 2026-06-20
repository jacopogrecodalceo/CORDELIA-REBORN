import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erf

def hc_hanning_curve(t):
    """Hanning (Hann) window curve"""
    return 0.5 * (1 - np.cos(2 * np.pi * t))

def hc_kiss_curve(t):
    """Kiss curve (smooth step)"""
    return t * t * (3 - 2 * t)

def hc_gaussian_curve(t, sigma, mu):
    """Gaussian curve"""
    return np.exp(-((t - mu) ** 2) / (2 * sigma ** 2))

def hc_gen(duration, segments):
    """
    Generate a piecewise curve from segments.
    
    Args:
        duration: Total duration
        segments: List of (fraction, target_value, curve_function) tuples
    
    Returns:
        Array of y values
    """
    points = 1024
    x = np.linspace(0, duration, points)
    y = np.zeros(points)
    
    # Start with 0
    current_value = 0
    current_time = 0
    
    # Normalize fractions so they sum to 1
    total_fraction = sum(seg[0] for seg in segments)
    
    for fraction, target_value, curve_func in segments:
        # Normalize fraction
        frac = fraction / total_fraction
        
        # Calculate segment duration
        seg_duration = duration * frac
        
        # Generate time points for this segment
        t = np.linspace(0, 1, int(points * frac))
        
        # Apply curve
        curve = curve_func(t)
        
        # Scale from current_value to target_value
        seg_values = current_value + (target_value - current_value) * curve
        
        # Place in output array
        start_idx = int(current_time / duration * points)
        end_idx = int((current_time + seg_duration) / duration * points)
        
        if end_idx - start_idx == len(seg_values):
            y[start_idx:end_idx] = seg_values
        else:
            # Handle edge cases with interpolation
            y[start_idx:end_idx] = np.interp(
                np.linspace(0, 1, end_idx - start_idx),
                np.linspace(0, 1, len(seg_values)),
                seg_values
            )
        
        current_time += seg_duration
        current_value = target_value
    
    return x, y

# Define the curve
duration = 1.0
segments = [
    (19/34, 1.0, hc_hanning_curve),
    (9/34, 0.73206, hc_kiss_curve),
    (5/34, 0.0, lambda t: hc_gaussian_curve(t, 0.86435, 2.96376))
]

# Generate the curve
x, y = hc_gen(duration, segments)

# Print all y values
print("Y values:")
for i, val in enumerate(y):
    print(f"x={x[i]:.6f}, y={val:.6f}")

# Print as Python list
print("\n\nY values as Python list:")
print(y.tolist())

# Plot the curve
plt.figure(figsize=(12, 6))
plt.plot(x, y, linewidth=2)
plt.title('Piecewise Curve with Hanning, Kiss, and Gaussian Segments')
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.grid(True, alpha=0.3)

# Mark segment boundaries
segment_x = [0]
for frac, _, _ in segments:
    segment_x.append(segment_x[-1] + frac / sum(s[0] for s in segments) * duration)
for x_pos in segment_x:
    plt.axvline(x=x_pos, color='red', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('curve.png', dpi=150)
plt.show()

print("\nCurve saved as 'curve.png'")