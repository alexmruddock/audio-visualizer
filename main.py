"""
Main application entry point for audio visualizer.
"""

import sys
import time
import numpy as np
import logging
from audio_capture import AudioCapture
from audio_analyzer import AudioAnalyzer
from visualizer import Visualizer

try:
    from config import Config
except ImportError:
    Config = None

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main application loop."""
    print("Initializing Audio Visualizer...")
    
    # Load configuration
    config = Config() if Config else None
    
    try:
        # Initialize components with config
        if config:
            audio_capture = AudioCapture(
                sample_rate=config.audio.sample_rate,
                frames_per_buffer=config.audio.frames_per_buffer
            )
            audio_analyzer = AudioAnalyzer(
                sample_rate=config.audio.sample_rate,
                config=config
            )
            visualizer = Visualizer(
                width=config.visualizer.width,
                height=config.visualizer.height
            )
        else:
            # Fallback to defaults if config not available
            logger.warning("Config module not found, using defaults")
            audio_capture = AudioCapture(sample_rate=44100, frames_per_buffer=1024)
            audio_analyzer = AudioAnalyzer(sample_rate=44100)
            visualizer = Visualizer(width=1280, height=720)
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        print(f"\nError initializing visualizer: {e}")
        return
    
    try:
        # List available devices
        print("\nAvailable audio input devices:")
        devices = audio_capture.list_devices()
        for idx, name in devices:
            marker = " <-- BlackHole" if 'blackhole' in name.lower() else ""
            print(f"  [{idx}] {name}{marker}")
        
        # Start audio stream
        print("\nStarting audio capture...")
        try:
            audio_capture.start_stream()
            print("Audio capture started successfully!")
        except RuntimeError as e:
            print(f"\nError: {e}")
            print("\nPlease ensure:")
            print("  1. BlackHole is installed (https://github.com/ExistentialAudio/BlackHole)")
            print("  2. A Multi-Output Device is configured in Audio MIDI Setup")
            print("  3. The Multi-Output Device includes BlackHole and your speakers")
            print("  4. System audio is set to use the Multi-Output Device")
            return
        
        print("\nVisualizer started! Press ESC or close window to exit.")
        print("Play some music and watch the visualization sync to the BPM.\n")
        
        # Main loop (optimized)
        running = True
        frame_count = 0
        last_debug_time = time.time()
        
        while running:
            # Handle events
            running = visualizer.handle_events()
            if not running:
                break
            
            # Read audio data
            try:
                samples = audio_capture.read_chunk()
            except RuntimeError as e:
                logger.error(f"Audio read error: {e}")
                print(f"\nError reading audio: {e}")
                print("Trying to recover...")
                time.sleep(0.1)
                continue
            except Exception as e:
                logger.error(f"Unexpected error reading audio: {e}")
                print(f"\nUnexpected error: {e}")
                break
            
            # Debug: Print audio level every 5 seconds (less frequent)
            frame_count += 1
            current_time = time.time()
            if current_time - last_debug_time >= 5.0:
                try:
                    audio_level = np.abs(samples).mean()
                    max_level = np.abs(samples).max()
                    print(f"Audio level: avg={audio_level:.4f}, max={max_level:.4f} " +
                          f"(silence if < 0.001)")
                    if audio_level < 0.001:
                        print("⚠️  No audio detected! Make sure:")
                        print("   1. Multi-Output Device is configured in Audio MIDI Setup")
                        print("   2. System audio output is set to Multi-Output Device")
                        print("   3. Music is playing")
                except Exception as e:
                    logger.warning(f"Error calculating audio level: {e}")
                last_debug_time = current_time
            
            # Analyze audio
            try:
                is_beat, bpm, features = audio_analyzer.process_audio(samples)
            except ValueError as e:
                logger.warning(f"Audio analysis error: {e}")
                # Continue with default values
                is_beat = False
                bpm = 0.0
                features = {}
            except Exception as e:
                logger.error(f"Unexpected error analyzing audio: {e}")
                is_beat = False
                bpm = 0.0
                features = {}
            
            # Update visualization
            try:
                visualizer.update(bpm, is_beat, features)
            except Exception as e:
                logger.error(f"Error updating visualizer: {e}")
                # Continue anyway
            
            # Render
            try:
                visualizer.render()
            except Exception as e:
                logger.error(f"Error rendering: {e}")
                # Try to recover by resetting current mode
                try:
                    current_mode = visualizer.mode_instances[visualizer.current_mode]
                    current_mode.reset()
                except:
                    pass
            
            # Let pygame clock handle timing (removed sleep for better performance)
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\nCleaning up...")
        audio_capture.cleanup()
        visualizer.cleanup()
        print("Done!")


if __name__ == "__main__":
    main()

