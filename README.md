# Audio Visualizer with BPM Detection

A Python-based audio visualizer that captures system audio (Spotify, etc.) and creates real-time visualizations synchronized to the music's BPM and frequency spectrum.

## Features

- 🎵 Captures internal system audio via BlackHole
- 🎯 Real-time BPM detection using advanced audio analysis
- 🎨 8 different visualization modes:
  - Particles - Fluid particle effects
  - Frequency Bars - Multi-band frequency visualization
  - Waveform - Professional oscilloscope-style display
  - Circles - Pulsing concentric circles
  - Matrix - Digital rain effect
  - Robot Face - Geometric face with strobe effects
  - Fractal - Julia set fractals that morph with audio
  - Spectrum Analyzer - Full-spectrum frequency analyzer
- 🌈 Frequency-reactive colors and animations
- ⚡ Low-latency real-time processing
- 🎛️ Professional-grade audio analysis with Hann windowing, spectral flux, and frequency-dependent smoothing

## Prerequisites

### macOS Setup

1. **Install BlackHole**
   - Download from: https://github.com/ExistentialAudio/BlackHole/releases
   - Install the `.pkg` file
   - Restart your Mac if prompted

2. **Configure Multi-Output Device**
   - Open **Audio MIDI Setup** (Applications > Utilities)
   - Click the **"+"** button at the bottom left
   - Select **"Create Multi-Output Device"**
   - In the right pane, check:
     - **BlackHole 2ch** (or your installed BlackHole channel)
     - Your built-in output (e.g., "MacBook Pro Speakers" or your headphones)
   - Right-click the Multi-Output Device and select **"Use This Device For Sound Output"**
   
   This allows you to hear audio while the visualizer captures it.

3. **Set Audio Output**
   - In System Preferences > Sound, select your Multi-Output Device as the output
   - Or use the Audio MIDI Setup as described above

### Python Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   All dependencies should install without system-level libraries. The project uses:
   - `sounddevice` - Easy audio capture (no system dependencies)
   - `numpy` - Audio processing and FFT
   - `pygame` - Visualization

   **Note:** Make sure to activate the virtual environment (`source venv/bin/activate`) before running the visualizer.

## Usage

1. **Activate the virtual environment** (if you created one)
   ```bash
   source venv/bin/activate
   ```

2. **Start the visualizer**
   ```bash
   python main.py
   ```

3. **Play music**
   - Start playing music in Spotify or any other app
   - The visualizer will automatically detect the audio and visualize it

4. **Controls**
   - Press **1-8** to switch between visualization modes
   - Press **ESC** or close the window to exit
   - The visualizer will automatically detect BPM and sync visuals
   - Window is resizable - drag to resize

## How It Works

1. **Audio Capture**: Uses `sounddevice` to capture audio from the BlackHole virtual audio device
2. **BPM Detection**: Uses advanced onset detection combining energy analysis, spectral flux, and autocorrelation to calculate BPM in real-time
3. **Frequency Analysis**: Analyzes audio frequencies using FFT with Hann windowing:
   - 7 frequency bands: sub-bass, bass, low-mid, mid, high-mid, treble, high-treble
   - Frequency-dependent smoothing for accurate visualization
   - Volume normalization for consistent response
4. **Visualization**: Modular system with 8 visualization modes:
   - Each mode reacts to audio features (BPM, beats, frequency bands)
   - Smooth mode switching with state management
   - Professional visual effects with grids, gradients, and peak holds

## Troubleshooting

### "BlackHole device not found"
- Ensure BlackHole is installed and a Multi-Output Device is configured
- Check that your system audio output is set to the Multi-Output Device
- Run the visualizer to see available devices listed

### No audio detected
- Verify audio is playing and system output is set correctly
- Check Audio MIDI Setup to ensure BlackHole is included in Multi-Output Device
- Try restarting the visualizer

### Performance issues
- Reduce `max_particles` in `modes/particles_mode.py` if needed
- Adjust `frames_per_buffer` in `audio_capture.py` (larger = less CPU but more latency)
- Some modes (fractal, spectrum) are more CPU-intensive than others

### Installation issues
- All dependencies should install directly via pip without system libraries
- If you encounter issues, ensure you have Python 3.8+ and pip updated: `pip install --upgrade pip`

## Project Structure

```
visualizer/
├── modes/              # Visualization mode implementations
│   ├── base.py        # Base class for all modes
│   ├── particles_mode.py
│   ├── frequency_bars_mode.py
│   ├── waveform_mode.py
│   ├── circles_mode.py
│   ├── matrix_mode.py
│   ├── robot_face_mode.py
│   ├── fractal_mode.py
│   └── spectrum_mode.py
├── constants.py       # Centralized constants (colors, sizes)
├── utils.py           # Shared utility functions
├── particles.py       # Particle class
├── audio_capture.py   # Audio input handling
├── audio_analyzer.py  # BPM detection and frequency analysis
├── visualizer.py      # Main visualization coordinator
└── main.py            # Application entry point
```

## Customization

You can customize the visualizer by editing:

- **`constants.py`**: Colors, sizes, thresholds, and visual parameters
- **`modes/*.py`**: Individual visualization mode behavior
- **`audio_analyzer.py`**: Frequency bands, BPM detection sensitivity
- **`config.py`**: Audio and visualization settings
- **`main.py`**: Window size, frame rate, etc.

## License

This project is provided as-is for personal use.

