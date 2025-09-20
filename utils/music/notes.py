import math


# Notes will always represent midi numbers
# Pitch classes are understood modulo 12, starting with C and wrapping to B
# Indices 0 to 11 map between C-1 to B-1, the negative-indexed octave -1,
# so never used in practice as notes, but are useful numeric counterparts for the pitch classes

Note = int
Octave = int

PITCH_CLASSES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NATURAL_CLASSES = ["C", "D", "E", "F", "G", "A", "B"]
ACCIDENTAL_CLASSES = ["C#", "D#", "F#", "G#", "A#"]
NATURAL_INDICES = [0, 2, 4, 5, 7, 9, 11]
ACCIDENTAL_INDICES = [1, 3, 6, 8, 10]


def note_2_frecuency(n: Note) -> float:
	return 440 * 2 ** ((n - 69)/12)

def note_2_frecuency_int(n: Note) -> int:
	return int(round(note_2_frecuency(n)))

def is_natural(n: Note) -> bool:
	return n%12 in NATURAL_INDICES

def note_2_class(n: Note) -> str:
	return PITCH_CLASSES[n%12]

def note_2_octave(n: Note) -> Octave:
	return math.floor(n/12) - 1

def note_2_full_name(n: Note) -> str:
	return note_2_class(n) + str(note_2_octave(n))

def name_2_note(name: str) -> Note:
	if not name:
		raise ValueError("Note name cannot be empty")
	
	pitch_class, octave = (name[:-1], int(name[-1])) if name[-1].isdigit() else (name, 0)
	pitch_phase = PITCH_CLASSES.index(pitch_class)
	return (octave + 1) * 12 + pitch_phase

