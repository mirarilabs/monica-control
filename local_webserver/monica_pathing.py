#!/usr/bin/env python3
"""
Local Monica Pathing Processor
Processes song pathing locally instead of on the Pico for better performance
"""

import json
import math
from typing import List, Optional, Tuple, Union
from dataclasses import dataclass


@dataclass
class Chord:
    """Represents a chord with notes"""
    notes: List[str]
    
    @classmethod
    def from_text(cls, chord_text: str) -> 'Chord':
        """Create chord from text like 'C4_E4_G4'"""
        if not chord_text:
            return cls([])
        notes = chord_text.split('_')
        return cls(notes)
    
    def __str__(self):
        return '_'.join(self.notes) if self.notes else "None"


@dataclass
class Duty:
    """Represents a musical duty with timing and chord"""
    start_ms: int
    duration_ms: int
    chord: Optional[Chord]
    skid: int = 0
    volume_percent: Optional[int] = None
    
    @property
    def end_ms(self) -> int:
        return self.start_ms + self.duration_ms
    
    @property
    def is_silent(self) -> bool:
        return self.chord is None
    
    @classmethod
    def silence(cls, start_ms: int, duration_ms: int, volume_percent: Optional[int] = None) -> 'Duty':
        return cls(start_ms, duration_ms, None, volume_percent=volume_percent)
    
    @classmethod
    def fill_with_silence(cls, duties: List['Duty']) -> List['Duty']:
        """Fill gaps between duties with silence"""
        sequence = []
        time_ms = 0
        for duty in duties:
            if duty.start_ms < time_ms:
                raise ValueError(f"Inconsistent duty order: {duty} starts at {duty.start_ms} ms, but no action expected at least until {time_ms} ms.")
            
            if duty.start_ms > time_ms:
                sequence.append(cls.silence(time_ms, duty.start_ms - time_ms))
                time_ms = duty.start_ms
            
            sequence.append(duty)
            time_ms += duty.duration_ms
        
        return sequence
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'start_ms': self.start_ms,
            'duration_ms': self.duration_ms,
            'chord': str(self.chord) if self.chord else None,
            'skid': self.skid,
            'volume_percent': self.volume_percent
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Duty':
        """Create from dictionary"""
        chord = Chord.from_text(data['chord']) if data['chord'] else None
        return cls(data['start_ms'], data['duration_ms'], chord, data.get('skid', 0), data.get('volume_percent'))


class Wagon:
    """Represents Monica's wagon system for position management"""
    
    def __init__(self, valid_positions: int = 12):
        self.valid_positions = valid_positions
    
    def flight_time(self, from_pos: int, to_pos: int) -> float:
        """Calculate time needed to move between positions (simplified)"""
        distance = abs(to_pos - from_pos)
        # Simplified flight time calculation (adjust based on actual Monica specs)
        return distance * 50.0  # 50ms per position
    
    def covering_qualities(self, chord: Optional[Chord]) -> List[float]:
        """Calculate covering quality for each position (simplified)"""
        if not chord or not chord.notes:
            return [0.0] * self.valid_positions
        
        # Simplified quality calculation - in real Monica this would be more complex
        # For now, return a basic quality distribution
        qualities = []
        for pos in range(self.valid_positions):
            # Basic quality based on position (higher positions for higher notes)
            base_quality = 1.0 - (abs(pos - self.valid_positions // 2) / (self.valid_positions // 2))
            qualities.append(max(0.1, base_quality))
        
        return qualities


class Choice:
    """Represents a pathfinding choice"""
    
    def __init__(self, position: int, quality: float):
        self.position = position
        self.quality = quality


class Keystra:
    """Pathfinding optimizer for Monica"""
    
    def __init__(self, wagon: Wagon, notes_bonus: float = 1.0, skid_bonus: float = 0.5, 
                 move_penalty: float = 0.1, time_penalty: float = 0.01):
        self._wagon = wagon
        self._positions = wagon.valid_positions
        self._silence_quality = [0.0] * self._positions
        
        self._notes_bonus = notes_bonus
        self._skid_bonus = skid_bonus
        self._move_penalty = move_penalty
        self._time_penalty = time_penalty
    
    def choice_quality(self, prev_time_ms: int, next_time_ms: int, prev_pos: int, 
                      next_pos: int, covering_quality: float, skid: int) -> float:
        """Calculate quality of a path choice"""
        quality = 0.0
        
        # Bias towards balanced trajectories across time
        delta_time = (next_time_ms - prev_time_ms) / 1000.0
        delta_pos = next_pos - prev_pos
        quality -= math.sqrt(self._move_penalty * delta_pos**2 + self._time_penalty * delta_time**2)
        
        flight_time = self._wagon.flight_time(prev_pos, next_pos)
        if flight_time > delta_time:
            return -float('inf')
        
        # If the skid is not valid, no key will be pressed if this path is chosen later on
        wanted_skid = delta_pos == skid
        no_skid = delta_pos == 0
        valid_skid = wanted_skid or no_skid
        if valid_skid and covering_quality > 0:
            quality += (delta_time + 1) * (self._notes_bonus * (covering_quality + 1) + wanted_skid * self._skid_bonus)
        
        return quality
    
    def fill_and_explore(self, duties: List[Duty]) -> Tuple[List[Duty], List[int]]:
        """Complete sequence with silences and find optimal path"""
        duties = Duty.fill_with_silence(duties)
        choices = [[Choice(-1, 0) for _ in range(self._positions)]]
        
        for duty in duties:
            next_choices = []
            covering_qualities = self._wagon.covering_qualities(duty.chord)
            
            for next_pos in range(self._positions):
                max_path = -1
                max_quality = -float('inf')
                
                for prev_pos in range(self._positions):
                    choice_quality = self.choice_quality(
                        duty.start_ms, duty.end_ms, prev_pos, next_pos, 
                        covering_qualities[prev_pos], duty.skid
                    )
                    path_quality = choices[-1][prev_pos].quality + choice_quality
                    
                    if path_quality > max_quality:
                        max_path = prev_pos
                        max_quality = path_quality
                
                next_choices.append(Choice(max_path, max_quality))
            
            choices.append(next_choices)
        
        # Backtrace to find optimal path
        path = [-1] * len(choices)
        path[-1] = max(range(self._positions), key=lambda pos: choices[-1][pos].quality)
        
        for i in range(len(choices) - 1, 0, -1):
            path[i - 1] = choices[i][path[i]].position
        
        return duties, path


class SongPlanner:
    """Local song planner for Monica"""
    
    def __init__(self):
        self.wagon = Wagon()
        self.keystra = Keystra(self.wagon)
    
    def plan_song_by_name(self, song_name: str = "showcase") -> Tuple[List[dict], List[int]]:
        """Plan a specific song by name and return serialized data"""
        songs = {
            "showcase": self._monica_showcase,
            "original": self._por_lo_que_yo_te_quiero,
            "simple": self._song1,
            "range_test": self._song6
        }
        
        if song_name not in songs:
            print(f"Unknown song '{song_name}'. Available: {list(songs.keys())}")
            song_name = "showcase"
        
        print(f"=== Planning song locally: {song_name} ===")
        song_func = songs[song_name]
        s = song_func()
        print(f"Song length: {len(s)} duties")
        
        duties, path = self.keystra.fill_and_explore(s)
        print(f"Planned: {len(duties)} duties, {len(path)} positions")
        print(f"Performance time: ~{duties[-1].end_ms/1000:.1f} seconds")
        print(f"Cart positions used: {sorted(set(path))}")
        
        # Convert duties to serializable format
        duties_dict = [duty.to_dict() for duty in duties]
        
        return duties_dict, path
    
    def _song1(self) -> List[Duty]:
        """Simple test song"""
        chords = [
            Chord.from_text("B3_D4_F#4"),
            Chord.from_text("G3_B3_D4"),
            Chord.from_text("D3_F#3_A3"),
            Chord.from_text("A3_C#4_E4"),
            Chord.from_text("B3_D4_F#4"),
            Chord.from_text("G3_B3_D4"),
            Chord.from_text("D3_F#3_A3"),
            Chord.from_text("A3_C#4_E4"),
            Chord.from_text("A5")
        ]
        # Add volume variations: soft start, building, peak, gentle ending
        volumes = [40, 50, 60, 70, 80, 75, 65, 55, 90]  # Peak on final high note
        return [Duty(i * 2175, 1800, chords[i], volume_percent=volumes[i]) for i in range(len(chords))]
    
    def _song6(self) -> List[Duty]:
        """Range test song"""
        chords = [
            Chord.from_text("F3"),
            Chord.from_text("C6"),
            Chord.from_text("F3"),
            Chord.from_text("C6"),
            Chord.from_text("C5")
        ]
        # Volume variations for range test: crescendo pattern
        volumes = [50, 70, 60, 80, 75]
        return [Duty(i * 2000, 1000, chords[i], volume_percent=volumes[i]) for i in range(len(chords))]
    
    def _por_lo_que_yo_te_quiero(self) -> List[Duty]:
        """Original Monica song"""
        tempo = 1500
        base_wait = 150
        # Format: (chord_text, duration, wait, volume_percent)
        progression = [
            ("D4_F4_A4", tempo, 0, 40),  # Soft start
            ("D4_F4_A#3", tempo, 0, 45),  # Building
            ("C4_E4_G4", tempo, 100, 60),  # Crescendo
            ("C5_F4_A4", tempo, 100, 70),  # Forte
            ("D4_G4_A#4", tempo, 50, 65),  # Slight decrease
            ("D5_F4_A4", tempo, 100, 75),  # Building again
            ("D4_E4_G#4_B4", tempo, 0, 50),  # Softer
            ("C#4_E4_G4_A4", tempo, 0, 55),  # Gentle
            ("D4_F4_A4", tempo, 100, 70),  # Return to forte
            ("D4_F4_A#4", tempo, 100, 75),  # Building
            ("C4_E4_G3", tempo, 0, 60),  # Lower register, softer
            ("C4_F4_A3", tempo, 100, 70),  # Building
            ("D4_G4_A#3", tempo, 100, 80),  # Peak volume
            ("D4_F4_A4", tempo, 100, 85),  # Fortissimo
            ("D4_E4_G#4_B4", 750, 0, 70),  # Gentle ending
            ("E4_A4_C#5", 750, 0, 60),  # Softer
            ("D4_F4_A4", tempo, 0, 50)  # Final soft chord
        ]
        
        duties = []
        start_time = 0
        for i in range(len(progression)):
            post_wait = base_wait + progression[i][2]
            volume_percent = progression[i][3]
            duties.append(Duty(start_time, progression[i][1] - post_wait, Chord.from_text(progression[i][0]), volume_percent=volume_percent))
            start_time += progression[i][1]
        
        return duties
    
    def _monica_showcase(self) -> List[Duty]:
        """Monica showcase song with volume dynamics"""
        musical_sequence = [
            # Opening - Low register exploration (positions 0-2) - Soft start
            ("F3", 0, 800, 30, "Single low note - soft start"),
            (None, 800, 200, None, "Breath"),
            ("G3_B3", 1000, 1000, 40, "Simple chord - building"),
            (None, 2000, 300, None, "Move to next position"),
            
            ("A3", 2300, 600, 50, "Single note higher - normal volume"),
            ("A3_C4_E4", 2900, 1200, 60, "Major chord - crescendo"),
            (None, 4100, 400, None, "Breath and move"),
            
            # Middle register - more complex (positions 3-5) - Building intensity
            ("C4_E4_G4", 4500, 800, 70, "C major chord - forte"),
            ("D4", 5300, 400, 60, "Single note - mezzo"),
            ("E4", 5700, 400, 70, "Single note - forte"),
            ("F4_A4_C5", 6100, 1000, 80, "F major chord - fortissimo"),
            (None, 7100, 300, None, "Breath"),
            
            # Rhythmic section - quick changes (positions 6-8) - Dynamic contrast
            ("G4", 7400, 300, 50, "Quick single - piano"),
            ("A4", 7700, 300, 60, "Quick single - mezzo"),
            ("B4", 8000, 300, 70, "Quick single - forte"),
            ("C5", 8300, 600, 85, "Sustained single - fortissimo"),
            (None, 8900, 200, None, "Quick breath"),
            
            ("G4_B4_D5", 9100, 800, 75, "G major chord - forte"),
            ("A4_C5_E5", 9900, 800, 65, "A minor chord - mezzo-forte"),
            (None, 10700, 400, None, "Move to high register"),
            
            # High register showcase (positions 9-11) - Peak intensity
            ("B4_D5_F5", 11100, 1000, 90, "High chord - maximum volume"),
            ("C5", 12100, 500, 85, "High single note - forte"),
            ("D5", 12600, 500, 90, "Higher single - fortissimo"),
            ("E5", 13100, 800, 95, "Even higher - peak volume"),
            (None, 13900, 300, None, "Final breath"),
            
            # Grand finale - full range sweep - Climax
            ("F5_A5_C6", 14200, 1200, 100, "Highest chord - maximum fortissimo"),
            ("C6", 15400, 1000, 95, "Highest single note - sustained"),
            (None, 16400, 500, None, "Final pause"),
            
            # Ending - return to middle - Gentle conclusion
            ("C4_E4_G4_C5", 16900, 1500, 70, "Final chord - wide voicing, mezzo-forte"),
        ]
        
        # Convert to Duty objects
        duties = []
        for chord_text, start_time, duration, volume_percent, description in musical_sequence:
            if chord_text is None:
                duty = Duty.silence(start_time, duration, volume_percent)
            else:
                chord = Chord.from_text(chord_text)
                duty = Duty(start_time, duration, chord, volume_percent=volume_percent)
            duties.append(duty)
        
        print(f"Monica showcase song created: {len(duties)} duties, {duties[-1].end_ms/1000:.1f} seconds")
        return duties


# Global instance
song_planner = SongPlanner()


