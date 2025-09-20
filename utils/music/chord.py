from utils.music.notes import *
from utils.iterables import iterable_arguments


class Chord:
	INTERVALS = {
		"single": {0},
		"fifth": {0, 7},
		"octave": {0, 12},

		"major": {0, 4, 7},
		"minor": {0, 3, 7},
		"diminished": {0, 3, 6},
		"augmented": {0, 4, 8},
		"major7": {0, 4, 7, 11},
		"minor7": {0, 3, 7, 10},
		"dominant7": {0, 4, 7, 10},
		}

	def __init__(self, *notes):
		if not notes:
			raise TypeError("No notes provided")
		
		self._notes: set[Note] = set(iterable_arguments(notes))
		
		if not all(isinstance(n, int) for n in self._notes):
			raise ValueError("All notes should be intergers")

	@property
	def notes(self):
		return self._notes

	@property
	def first_note(self):
		return sorted(self._notes)[0]

	@property
	def last_note(self):
		return sorted(self._notes)[-1]

	def overlaps(self, other: 'Chord | set[Note]'):
		other_notes = other.notes if isinstance(other, Chord) else other
		return not self._notes.isdisjoint(other_notes)

	@classmethod
	def from_intervals(cls, root_note, chord_type):
		if not isinstance(root_note, int):
			raise TypeError("root_note should be an int")
		
		if not isinstance(chord_type, str):
			raise TypeError("chord_type should be a string")

		intervals = cls.INTERVALS[chord_type]
		return cls(root_note + i for i in intervals)

	@classmethod
	def from_text(cls, text):
		return cls(name_2_note(name) for name in text.split("_"))

	def __str__(self) -> str:
		return '_'.join(note_2_full_name(n) for n in sorted(self.notes))
	
	def __repr__(self) -> str:
		return self.__str__()

	def __eq__(self, other):
		return isinstance(other, Chord) and self.notes == other.notes

	def __add__(self, semitones):
		if not isinstance(semitones, int):
			return NotImplemented
		
		return Chord(n + semitones for n in self._notes)

	def __sub__(self, semitones: int):
		return self + (-semitones)

	def __and__(self, other):
		if not isinstance(other, Chord):
			return NotImplemented
		
		return Chord(self._notes & other._notes)

	def __or__(self, other):
		if not isinstance(other, Chord):
			return NotImplemented
		
		return Chord(self._notes | other._notes)

	def __contains__(self, note):
		return note in self._notes

