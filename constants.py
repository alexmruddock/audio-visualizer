"""
Constants for visualization system.
"""

from typing import Tuple, Dict

# Colors
COLOR_BACKGROUND_DARK = (8, 8, 12)
COLOR_BACKGROUND_WAVEFORM = (5, 5, 10)
COLOR_BACKGROUND_BLACK = (0, 0, 0)

COLOR_GRID = (25, 30, 35)
COLOR_GRID_WAVEFORM = (20, 30, 40)
COLOR_CENTER_LINE = (30, 50, 70)

COLOR_TEXT_PRIMARY = (200, 200, 200)
COLOR_TEXT_SECONDARY = (150, 150, 150)
COLOR_TEXT_DIM = (120, 130, 140)
COLOR_TEXT_WHITE = (255, 255, 255)

COLOR_OVERLAY_BG = (5, 5, 10)
COLOR_OVERLAY_ALPHA = 200

# Frequency band colors
BAND_COLORS: Dict[str, Tuple[int, int, int]] = {
    'sub_bass': (180, 0, 100),      # Deep purple/red
    'bass': (255, 50, 50),          # Red
    'low_mid': (255, 150, 0),       # Orange
    'mid': (255, 255, 50),          # Yellow
    'high_mid': (100, 255, 100),    # Green
    'treble': (50, 150, 255),       # Blue
    'high_treble': (150, 50, 255),  # Purple
}

# Frequency band positions (0.0 to 1.0 across screen width)
BAND_POSITIONS: Dict[str, float] = {
    'sub_bass': 0.0,
    'bass': 0.14,
    'low_mid': 0.28,
    'mid': 0.42,
    'high_mid': 0.57,
    'treble': 0.71,
    'high_treble': 0.85,
}

# Frequency band labels
BAND_LABELS: Dict[str, str] = {
    'sub_bass': 'Sub',
    'bass': 'Bass',
    'low_mid': 'Low-Mid',
    'mid': 'Mid',
    'high_mid': 'High-Mid',
    'treble': 'Treble',
    'high_treble': 'High',
}

# Smoothing factors (frequency-dependent)
SMOOTHING_FACTORS: Dict[str, float] = {
    'sub_bass': 0.85,    # Fast smoothing for transients
    'bass': 0.85,        # Fast smoothing for kick drums
    'low_mid': 0.90,     # Medium smoothing
    'mid': 0.92,         # Medium-slow smoothing
    'high_mid': 0.94,    # Slow smoothing
    'treble': 0.95,      # Very slow smoothing
    'high_treble': 0.96, # Very slow smoothing
}

# UI Constants
FONT_SIZE_LARGE = 36
FONT_SIZE_MEDIUM = 22
FONT_SIZE_SMALL = 18
FONT_SIZE_TINY = 24

OVERLAY_MARGIN = 10
OVERLAY_WIDTH = 250
OVERLAY_HEIGHT_BASIC = 100
OVERLAY_HEIGHT_TALL = 115

HELP_TEXT_Y_OFFSET = 25
HELP_TEXT_Y_OFFSET_SPECTRUM = 45

# Rendering constants
BAR_BOTTOM_FRACTION = 0.85  # Bars start at 85% of screen height
BAR_HEIGHT_FRACTION = 0.8    # Bars can use 80% of screen height
WAVEFORM_SCALE_FACTOR = 0.35  # Waveform uses 35% of screen height
WAVEFORM_MARGIN = 10

PEAK_HOLD_DECAY = 0.96  # Peak hold decay factor
MAX_ENERGY_DECAY = 0.9995  # Max energy decay for adaptive scaling

# Spectrum analyzer
SPECTRUM_MAX_BARS = 400
SPECTRUM_LOG_SCALE = True
SPECTRUM_PEAK_HOLD_DECAY = 0.97

# Frequency labels for spectrum
SPECTRUM_FREQUENCY_LABELS = [
    ('20Hz', 0.0),
    ('100Hz', 0.12),
    ('500Hz', 0.25),
    ('1kHz', 0.35),
    ('5kHz', 0.55),
    ('10kHz', 0.72),
    ('20kHz', 0.95),
]

# Particle system
PARTICLE_MAX_COUNT = 500
PARTICLE_TRAIL_ALPHA = 200
PARTICLE_TRAIL_FADE = 10

# Waveform
WAVEFORM_MAX_LENGTH = 1000
WAVEFORM_RESET_INTERVAL = 5.0  # seconds
WAVEFORM_PEAK_DECAY = 0.98

# Matrix
MATRIX_CHAR_ALPHABET = '0123456789ABCDEF'
MATRIX_LIFE_DECAY = 0.01

# Fractal
FRACTAL_JULIA_C_DEFAULT = complex(-0.7, 0.27015)
FRACTAL_ITERATIONS_DEFAULT = 50
FRACTAL_ITERATIONS_MIN = 30
FRACTAL_ITERATIONS_MAX = 100
FRACTAL_ZOOM = 1.5

# Robot face
STROBE_DECAY = 0.85
STROBE_THRESHOLD = 0.1

# Beat detection
BEAT_FLASH_ALPHA = 120
BEAT_FLASH_HEIGHT_FACTOR = 1.15

# Grid
GRID_HORIZONTAL_LINES = 5
GRID_VERTICAL_DIVISIONS = 10

