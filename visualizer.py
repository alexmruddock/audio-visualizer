"""
Visualization engine for rendering particle and fluid effects.
"""

import pygame
from typing import List
from modes import (
    ParticlesMode, FrequencyBarsMode, WaveformMode, CirclesMode,
    MatrixMode, RobotFaceMode, FractalMode, SpectrumMode
)
from constants import (
    COLOR_TEXT_SECONDARY, COLOR_TEXT_PRIMARY, COLOR_TEXT_WHITE,
    FONT_SIZE_LARGE, FONT_SIZE_TINY, HELP_TEXT_Y_OFFSET, HELP_TEXT_Y_OFFSET_SPECTRUM
)


class Visualizer:
    """Main visualization engine."""
    
    def __init__(self, width: int = 1280, height: int = 720):
        """
        Initialize visualizer.
        
        Args:
            width: Window width
            height: Window height
        """
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Audio Visualizer")
        
        # Initialize all visualization modes
        self.mode_instances = [
            ParticlesMode(width, height),
            FrequencyBarsMode(width, height),
            WaveformMode(width, height),
            CirclesMode(width, height),
            MatrixMode(width, height),
            RobotFaceMode(width, height),
            FractalMode(width, height),
            SpectrumMode(width, height),
        ]
        
        # Mode names for display
        self.mode_names = [
            'particles', 'frequency_bars', 'waveform', 'circles',
            'matrix', 'robot_face', 'fractal', 'spectrum'
        ]
        
        self.current_mode = 0  # Start with particles
        
        # Visual state (shared across modes)
        self.current_bpm = 0.0
        self.beat_triggered = False
        self.features = {
            'bass': 0.0,
            'mid': 0.0,
            'treble': 0.0,
            'total_energy': 0.0
        }
        
        self.clock = pygame.time.Clock()
    
    def update(self, bpm: float, is_beat: bool, features: dict) -> None:
        """
        Update visualizer state.
        
        Args:
            bpm: Current BPM
            is_beat: Whether a beat was detected
            features: Audio features dictionary
        """
        self.current_bpm = bpm
        self.features = features
        self.beat_triggered = is_beat
        
        dt = self.clock.tick(60) / 1000.0
        
        # Update current mode
        current_mode_instance = self.mode_instances[self.current_mode]
        try:
            current_mode_instance.update(dt, bpm, is_beat, features)
        except Exception as e:
            import sys
            print(f"Error updating mode '{self.mode_names[self.current_mode]}': {e}", file=sys.stderr)
    
    def render(self) -> None:
        """Render the visualization based on current mode."""
        mode_name = self.mode_names[self.current_mode]
        current_mode_instance = self.mode_instances[self.current_mode]
        
        try:
            # Render the current mode
            current_mode_instance.render(self.screen)
        except Exception as e:
            import sys
            print(f"Error rendering mode '{mode_name}': {e}", file=sys.stderr)
            # Fallback to particles mode
            if self.current_mode != 0:
                try:
                    self.mode_instances[0].render(self.screen)
                except:
                    self.screen.fill((50, 0, 0))
                    font = pygame.font.Font(None, 48)
                    error_text = font.render(f"Error rendering mode", True, (255, 0, 0))
                    self.screen.blit(error_text, (self.width // 2 - 200, self.height // 2))
        
        # Draw mode and BPM text (only for modes that don't have custom overlays)
        # Spectrum, waveform, and frequency_bars have their own info overlays
        if mode_name not in ['spectrum', 'waveform', 'frequency_bars']:
            font = pygame.font.Font(None, FONT_SIZE_LARGE)
            mode_text = font.render(
                f"Mode: {mode_name.replace('_', ' ').title()} ({self.current_mode + 1})",
                True, COLOR_TEXT_PRIMARY
            )
            self.screen.blit(mode_text, (10, 10))
            
            if self.current_bpm > 0:
                bpm_text = font.render(f"BPM: {int(self.current_bpm)}", True, COLOR_TEXT_WHITE)
                self.screen.blit(bpm_text, (10, 50))
        
        # Draw help text (positioned to avoid overlap)
        help_font = pygame.font.Font(None, FONT_SIZE_TINY)
        help_text = help_font.render("Press 1-8 to switch modes", True, COLOR_TEXT_SECONDARY)
        # Position help text at bottom-left, but leave space for frequency labels
        help_y = self.height - HELP_TEXT_Y_OFFSET if mode_name != 'spectrum' else self.height - HELP_TEXT_Y_OFFSET_SPECTRUM
        self.screen.blit(help_text, (10, help_y))
        
        pygame.display.flip()
    
    def handle_events(self) -> bool:
        """
        Handle pygame events.
        
        Returns:
            True if should continue running
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_1:
                    self._switch_mode(0)
                elif event.key == pygame.K_2:
                    self._switch_mode(1)
                elif event.key == pygame.K_3:
                    self._switch_mode(2)
                elif event.key == pygame.K_4:
                    self._switch_mode(3)
                elif event.key == pygame.K_5:
                    self._switch_mode(4)
                elif event.key == pygame.K_6:
                    self._switch_mode(5)
                elif event.key == pygame.K_7:
                    self._switch_mode(6)
                elif event.key == pygame.K_8:
                    self._switch_mode(7)
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                self.width = event.w
                self.height = event.h
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                # Update all modes with new size
                for mode in self.mode_instances:
                    mode.update_size(self.width, self.height)
        return True
    
    def _switch_mode(self, mode_index: int) -> None:
        """Switch to a different visualization mode."""
        if 0 <= mode_index < len(self.mode_instances):
            # Reset the old mode
            if self.current_mode < len(self.mode_instances):
                try:
                    self.mode_instances[self.current_mode].reset()
                except:
                    pass
            
            # Switch to new mode
            self.current_mode = mode_index
            
            # Reset the new mode
            try:
                self.mode_instances[mode_index].reset()
            except:
                pass
    
    def register_mode(self, name: str, mode_instance) -> None:
        """
        Register a new visualization mode.
        
        Args:
            name: Mode name (must be unique)
            mode_instance: Instance of VisualizationMode subclass
        """
        if name not in self.mode_names:
            self.mode_names.append(name)
            self.mode_instances.append(mode_instance)
        else:
            # Replace existing mode
            index = self.mode_names.index(name)
            self.mode_instances[index] = mode_instance
    
    def cleanup(self) -> None:
        """Clean up resources."""
        pygame.quit()
