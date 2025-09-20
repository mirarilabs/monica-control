from utils.music.notes import Note, note_2_full_name


# Keys represent indices of the virtual locations of notes (that might be empty)
Key = int

CYCLE_CLASSES = ["C", "C#", "D", "D#", "E", None, "F", "F#", "G", "G#", "A", "A#", "B", None]
CYCLE_INDICES = [0, 1, 2, 3, 4, None, 5, 6, 7, 8, 9, 10, 11, None]

# This is how a physical keyboard relates its keys to its notes (or lack of)
def keyboard_segment(start: Note, end: Note) -> list[Note | None]:
		notes: list[Note | None] = []
		n = start
		phase = CYCLE_INDICES.index(n%12)
		while n <= end:
			if CYCLE_INDICES[phase] is None:
				notes.append(None)
			else:
				notes.append(n)
				n += 1
			phase = (phase + 1)%14
		return notes

class Keyboard():
	def __init__(self, start: Note, end: Note) -> None:
		self._notes = keyboard_segment(start, end)

	def __str__(self) -> str:
		ljust3 = lambda s: s if len(s) >= 3 else s + ' '
		return "Keyboard: " + " ".join("___" if n is None else ljust3(note_2_full_name(n)) for n in self._notes)
	
	def __repr__(self) -> str:
		return self.__str__()

	@property
	def key_count(self):
		return len(self._notes)

	def get_note(self, i):
		return self._notes[i]

	@property
	def first_note(self):
		return self._notes[0]

	@property
	def last_note(self):
		return self._notes[-1]

