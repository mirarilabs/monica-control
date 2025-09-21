#!/usr/bin/env python3
"""
MIDI Processing Module for Monica
Converts MIDI files to Monica Duty objects for pathing
"""

import math
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from collections import defaultdict
import json

# Import Monica's existing classes
from monica_pathing import Chord, Duty, SongPlanner


@dataclass
class MIDINote:
    """Represents a MIDI note event"""
    note_number: int  # MIDI note number (0-127)
    velocity: int     # Note velocity (0-127)
    start_time: int   # Start time in MIDI ticks
    duration: int     # Duration in MIDI ticks
    channel: int      # MIDI channel


@dataclass
class MIDIChord:
    """Represents a chord (multiple simultaneous notes)"""
    notes: List[MIDINote]
    start_time: int
    duration: int
    velocity: int  # Average velocity of notes


class MIDINoteMapper:
    """Maps MIDI notes to Monica's note system"""
    
    # Monica's supported note range (based on showcase song analysis)
    MONICA_MIN_NOTE = 53  # F3 (MIDI note number)
    MONICA_MAX_NOTE = 84  # C6 (MIDI note number)
    
    # MIDI note number to Monica note name mapping
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    @classmethod
    def midi_to_monica_note(cls, midi_note: int) -> Optional[str]:
        """Convert MIDI note number to Monica note name"""
        if not cls.MONICA_MIN_NOTE <= midi_note <= cls.MONICA_MAX_NOTE:
            return None  # Note out of Monica's range
        
        octave = (midi_note // 12) - 1
        note_name = cls.NOTE_NAMES[midi_note % 12]
        return f"{note_name}{octave}"
    
    @classmethod
    def filter_notes_in_range(cls, notes: List[MIDINote]) -> List[MIDINote]:
        """Filter notes to only include those in Monica's range"""
        return [note for note in notes 
                if cls.MONICA_MIN_NOTE <= note.note_number <= cls.MONICA_MAX_NOTE]
    
    @classmethod
    def transpose_note(cls, note: MIDINote, semitones: int) -> MIDINote:
        """Transpose a MIDI note by semitones"""
        new_note_number = max(0, min(127, note.note_number + semitones))
        return MIDINote(
            note_number=new_note_number,
            velocity=note.velocity,
            start_time=note.start_time,
            duration=note.duration,
            channel=note.channel
        )


class MIDITimingConverter:
    """Converts MIDI timing to Monica's millisecond-based system"""
    
    @staticmethod
    def ticks_to_ms(ticks: int, ticks_per_quarter: int, tempo_bpm: int = 120) -> int:
        """Convert MIDI ticks to milliseconds"""
        # Standard formula: ms = (ticks / ticks_per_quarter) * (60000 / bpm)
        ms_per_tick = (60000.0 / tempo_bpm) / ticks_per_quarter
        return int(round(ticks * ms_per_tick))
    
    @staticmethod
    def velocity_to_volume(velocity: int) -> int:
        """Convert MIDI velocity (0-127) to Monica volume percentage (0-100)"""
        # Linear mapping: 0-127 -> 0-100
        return max(0, min(100, int(round((velocity / 127.0) * 100))))


class MIDIParser:
    """Parses MIDI files and extracts musical information"""
    
    def __init__(self):
        self.tempo_bpm = 120  # Default tempo
        self.ticks_per_quarter = 480  # Default PPQ
        
    def parse_midi_file(self, midi_file_path: str) -> Tuple[List[MIDINote], Dict]:
        """
        Parse MIDI file and extract note events
        Returns: (notes, metadata)
        """
        try:
            import mido
        except ImportError:
            raise ImportError("mido library required. Install with: pip install mido")
        
        notes = []
        metadata = {
            'tempo_bpm': self.tempo_bpm,
            'ticks_per_quarter': self.ticks_per_quarter,
            'tracks': 0,
            'duration_ticks': 0
        }
        
        mid = mido.MidiFile(midi_file_path)
        self.ticks_per_quarter = mid.ticks_per_beat
        metadata['ticks_per_quarter'] = self.ticks_per_quarter
        metadata['tracks'] = len(mid.tracks)
        
        current_time = 0
        active_notes = {}  # Track active notes for duration calculation
        
        for track in mid.tracks:
            track_time = 0
            
            for msg in track:
                track_time += msg.time
                
                if msg.type == 'set_tempo':
                    # Convert microseconds per quarter note to BPM
                    self.tempo_bpm = 60000000 / msg.tempo
                    metadata['tempo_bpm'] = self.tempo_bpm
                
                elif msg.type == 'note_on' and msg.velocity > 0:
                    # Note starts
                    note = MIDINote(
                        note_number=msg.note,
                        velocity=msg.velocity,
                        start_time=track_time,
                        duration=0,  # Will be set when note_off is received
                        channel=msg.channel
                    )
                    active_notes[msg.note] = note
                
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    # Note ends
                    if msg.note in active_notes:
                        note = active_notes[msg.note]
                        note.duration = track_time - note.start_time
                        notes.append(note)
                        del active_notes[msg.note]
        
        # Handle notes that don't have explicit note_off events
        for note in active_notes.values():
            note.duration = max(480, note.duration)  # Minimum duration of 1 beat
            notes.append(note)
        
        metadata['duration_ticks'] = max((note.start_time + note.duration for note in notes), default=0)
        
        return notes, metadata


class MIDIChordDetector:
    """Detects chords from MIDI note events"""
    
    def __init__(self, time_window_ms: int = 50):
        self.time_window_ms = time_window_ms  # Maximum time difference for chord notes
    
    def detect_chords(self, notes: List[MIDINote], timing_converter: MIDITimingConverter) -> List[MIDIChord]:
        """Group simultaneous notes into chords"""
        if not notes:
            return []
        
        # Convert timing to milliseconds for easier comparison
        ms_notes = []
        for note in notes:
            start_ms = timing_converter.ticks_to_ms(
                note.start_time, 
                timing_converter.ticks_per_quarter, 
                timing_converter.tempo_bpm
            )
            duration_ms = timing_converter.ticks_to_ms(
                note.duration,
                timing_converter.ticks_per_quarter,
                timing_converter.tempo_bpm
            )
            ms_notes.append(MIDINote(
                note_number=note.note_number,
                velocity=note.velocity,
                start_time=start_ms,
                duration=duration_ms,
                channel=note.channel
            ))
        
        # Sort notes by start time
        ms_notes.sort(key=lambda n: n.start_time)
        
        chords = []
        i = 0
        
        while i < len(ms_notes):
            # Find all notes that start within the time window
            chord_notes = [ms_notes[i]]
            j = i + 1
            
            while j < len(ms_notes) and ms_notes[j].start_time - ms_notes[i].start_time <= self.time_window_ms:
                chord_notes.append(ms_notes[j])
                j += 1
            
            # Create chord from simultaneous notes
            if len(chord_notes) == 1:
                # Single note - create single-note chord
                note = chord_notes[0]
                chord = MIDIChord(
                    notes=[note],
                    start_time=note.start_time,
                    duration=note.duration,
                    velocity=note.velocity
                )
            else:
                # Multiple notes - create chord
                avg_velocity = sum(n.velocity for n in chord_notes) // len(chord_notes)
                chord = MIDIChord(
                    notes=chord_notes,
                    start_time=chord_notes[0].start_time,
                    duration=max(n.duration for n in chord_notes),
                    velocity=avg_velocity
                )
            
            chords.append(chord)
            i = j
        
        return chords


class MIDIToDutyConverter:
    """Converts MIDI chords to Monica Duty objects"""
    
    def __init__(self, max_polyphony: int = 6, max_duties: int = 300):
        self.max_polyphony = max_polyphony  # Maximum simultaneous notes Monica can play
        self.max_duties = max_duties  # Maximum duties to prevent Pico memory issues (reduced for safety)
        self.note_mapper = MIDINoteMapper()
        self.timing_converter = MIDITimingConverter()
    
    def convert_to_duties(self, midi_file_path: str) -> Tuple[List[Duty], Dict]:
        """
        Convert MIDI file to Monica Duty objects
        Returns: (duties, metadata)
        """
        # Parse MIDI file
        parser = MIDIParser()
        notes, metadata = parser.parse_midi_file(midi_file_path)
        
        # Filter notes to Monica's range
        filtered_notes = self.note_mapper.filter_notes_in_range(notes)
        
        if not filtered_notes:
            raise ValueError("No notes found in Monica's supported range (F3-C6)")
        
        # Set timing converter parameters
        self.timing_converter.ticks_per_quarter = metadata['ticks_per_quarter']
        self.timing_converter.tempo_bpm = metadata['tempo_bpm']
        
        # Detect chords
        chord_detector = MIDIChordDetector()
        chords = chord_detector.detect_chords(filtered_notes, self.timing_converter)
        
        # Convert chords to duties
        duties = []
        for chord in chords:
            # Limit polyphony
            if len(chord.notes) > self.max_polyphony:
                # Keep highest priority notes (could be improved with better heuristics)
                chord.notes = chord.notes[:self.max_polyphony]
            
            # Convert MIDI notes to Monica note names and remove duplicates
            monica_notes = []
            for note in chord.notes:
                monica_note = self.note_mapper.midi_to_monica_note(note.note_number)
                if monica_note and monica_note not in monica_notes:
                    monica_notes.append(monica_note)
            
            if not monica_notes:
                continue  # Skip if no valid notes
            
            # Create chord
            if len(monica_notes) == 1:
                chord_text = monica_notes[0]
            else:
                chord_text = '_'.join(sorted(monica_notes))
            
            chord_obj = Chord.from_text(chord_text)
            
            # Convert velocity to volume
            volume_percent = self.timing_converter.velocity_to_volume(chord.velocity)
            
            # Create duty
            duty = Duty(
                start_ms=chord.start_time,
                duration_ms=chord.duration,
                chord=chord_obj,
                volume_percent=volume_percent
            )
            
            duties.append(duty)
        
        # Sort duties by start time to ensure chronological order
        duties.sort(key=lambda d: d.start_ms)
        
        # Resolve overlapping duties
        duties = self._resolve_overlapping_duties(duties)
        
        # Fill gaps with silence
        duties = Duty.fill_with_silence(duties)
        
        # Optimize duties if there are too many (for Pico memory limits)
        # Use more aggressive limit since pathing system may add more duties
        target_duties = max(150, self.max_duties // 2)  # Target half of limit for safety
        if len(duties) > target_duties:
            duties = self._optimize_duties(duties, target_duties)
        
        # Update metadata
        metadata['total_duties'] = len(duties)
        metadata['duration_ms'] = max((d.end_ms for d in duties), default=0)
        metadata['filtered_notes'] = len(filtered_notes)
        metadata['original_notes'] = len(notes)
        metadata['optimized'] = len(duties) < len(chords)  # Track if optimization occurred
        
        return duties, metadata
    
    def _resolve_overlapping_duties(self, duties: List[Duty]) -> List[Duty]:
        """Resolve overlapping duties by adjusting timing"""
        if not duties:
            return duties
        
        resolved_duties = []
        current_time = 0
        
        for i, duty in enumerate(duties):
            # If duty starts before current time, adjust it
            if duty.start_ms < current_time:
                # Calculate overlap
                overlap = current_time - duty.start_ms
                # Shorten the duty by the overlap amount, but keep minimum 50ms
                new_duration = max(50, duty.duration_ms - overlap)
                
                print(f"MIDI Processing: Resolved overlap for duty {i+1}: "
                      f"start {duty.start_ms}ms -> {current_time}ms, "
                      f"duration {duty.duration_ms}ms -> {new_duration}ms")
                
                duty = Duty(
                    start_ms=current_time,
                    duration_ms=new_duration,
                    chord=duty.chord,
                    skid=duty.skid,
                    volume_percent=duty.volume_percent
                )
            
            resolved_duties.append(duty)
            current_time = duty.end_ms
        
        return resolved_duties
    
    def _optimize_duties(self, duties: List[Duty], target_count: int = None) -> List[Duty]:
        """Optimize duties to reduce count while preserving musical content"""
        if target_count is None:
            target_count = self.max_duties
        
        if len(duties) <= target_count:
            return duties
        
        print(f"MIDI Processing: Optimizing {len(duties)} duties to {target_count} for Pico memory limits")
        
        # Strategy: Keep most important duties based on volume and duration
        # 1. Calculate importance score for each duty
        duty_scores = []
        for i, duty in enumerate(duties):
            score = 0
            
            # Higher volume = more important
            volume = duty.volume_percent or 50
            score += volume * 2
            
            # Longer duration = more important
            score += duty.duration_ms / 10
            
            # Musical content (non-silence) = more important
            if duty.chord is not None:
                score += 100
            
            # Bonus for sustained notes (longer than 200ms)
            if duty.duration_ms > 200:
                score += 50
            
            duty_scores.append((score, i, duty))
        
        # 2. Sort by importance score (highest first)
        duty_scores.sort(key=lambda x: x[0], reverse=True)
        
        # 3. Keep top duties and fill gaps
        kept_indices = set()
        optimized_duties = []
        
        # Keep top scoring duties
        for score, original_index, duty in duty_scores[:target_count]:
            kept_indices.add(original_index)
            optimized_duties.append(duty)
        
        # 4. Sort by time to maintain chronological order
        optimized_duties.sort(key=lambda d: d.start_ms)
        
        print(f"MIDI Processing: Reduced from {len(duties)} to {len(optimized_duties)} duties")
        print(f"MIDI Processing: Kept {(len(optimized_duties)/len(duties)*100):.1f}% of original duties")
        
        return optimized_duties


class MIDIProcessor:
    """Main interface for MIDI processing"""
    
    def __init__(self):
        self.converter = MIDIToDutyConverter()
    
    def process_midi_file(self, midi_file_path: str) -> Tuple[List[Duty], List[int], Dict]:
        """
        Process MIDI file and generate pathing
        Returns: (duties, path, metadata)
        """
        # Convert MIDI to duties
        duties, metadata = self.converter.convert_to_duties(midi_file_path)
        
        # Final safety check - if still too many duties, apply emergency optimization
        if len(duties) > 500:
            print(f"MIDI Processing: Emergency optimization - {len(duties)} duties still too many")
            duties = self.converter._optimize_duties(duties, 200)  # Emergency reduction
            metadata['total_duties'] = len(duties)
            metadata['optimized'] = True
        
        # Generate pathing using existing Monica pathing system
        song_planner = SongPlanner()
        duties_dict, path = song_planner.keystra.fill_and_explore(duties)
        
        # Convert duties to serializable format
        duties_dict = [duty.to_dict() for duty in duties_dict]
        
        # Final check on final duties count
        if len(duties_dict) > 500:
            print(f"MIDI Processing: WARNING - Final duty count {len(duties_dict)} may cause Pico memory issues")
        
        return duties_dict, path, metadata
    
    def get_midi_info(self, midi_file_path: str) -> Dict:
        """Get information about a MIDI file without full processing"""
        parser = MIDIParser()
        notes, metadata = parser.parse_midi_file(midi_file_path)
        
        # Add note statistics
        metadata['total_notes'] = len(notes)
        metadata['notes_in_range'] = len(MIDINoteMapper.filter_notes_in_range(notes))
        metadata['note_range'] = {
            'min': min((n.note_number for n in notes), default=0),
            'max': max((n.note_number for n in notes), default=0)
        }
        
        return metadata


# Global instance
midi_processor = MIDIProcessor()


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python midi_processor.py <midi_file>")
        sys.exit(1)
    
    midi_file = sys.argv[1]
    
    try:
        print(f"Processing MIDI file: {midi_file}")
        
        # Get file info
        info = midi_processor.get_midi_info(midi_file)
        print(f"MIDI Info: {json.dumps(info, indent=2)}")
        
        # Process file
        duties, path, metadata = midi_processor.process_midi_file(midi_file)
        
        print(f"\nProcessed {len(duties)} duties")
        print(f"Duration: {metadata['duration_ms']/1000:.1f} seconds")
        print(f"Notes in Monica range: {metadata['filtered_notes']}/{metadata['original_notes']}")
        
        # Show first few duties
        print("\nFirst 5 duties:")
        for i, duty in enumerate(duties[:5]):
            print(f"  {i+1}: {duty}")
        
    except Exception as e:
        print(f"Error processing MIDI file: {e}")
        sys.exit(1)
