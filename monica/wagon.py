from utils.music.keyboard import Keyboard, Key
from utils.music.notes import Note
from utils.music.chord import Chord


# Position is the wagon's position index, with 0 being the first white key. Every increment represent a shift of one white key (two Keyboard Keys)
Position = int
Quality = float

# This is the bridge between musical abstraction and physical world
class Wagon:
	def __init__(self, keyboard: Keyboard, flight_time, structure: list[list[Key]], valid_positions: int, wagon_2_stepper: float) -> None:
		self._keyboard = keyboard
		self._flight_time = flight_time
		self._structure = structure
		self._valid_positions = valid_positions
		self._wagon_2_stepper = wagon_2_stepper
		
		# The given structure is assumed to represent the actionable keys in the leftmost valid position
		# eg. normally it would start in 0, but if the first were a black key it should be 1 or -1 (-1 representing a legally out of bounds black key)
		# For each Position we translate the structure by two Keys (from white to white) and sample the actual note spans of each finger
		self._spans: list[list[list[Note]]] = [
				[
					[
						note for key in finger if isinstance(note := keyboard.get_note(2 * position + key), Note)
					] for finger in structure
				] for position in range(0, valid_positions)
			]

	@property
	def valid_positions(self) -> int:
		return self._valid_positions
	
	def calculate_steps(self, position: Position) -> float:
		return position * self._wagon_2_stepper

	def _span_quality(self, chord: Chord, span: list[list[Note]]) -> Quality:
		# Simple quality measure: how many notes can be played by a given span
		return sum(chord.overlaps(set(finger)) for finger in span)

	def covering_qualities(self, chord: Chord) -> list[Quality]:
		return list(self._span_quality(chord, span) for span in self._spans)
	
	# Given the intended chord and the wagon position, returns the best fingering choice for each finger
	def calculate_fingerings(self, chord: Chord, position: Position) -> list[int | None]:
		# Returns the index of the first finger that can play a note in the chord, if any
		# Used for telling what position the finger servo should go to
		def fingering(finger: list[Note]) -> int | None:
			for i, note in enumerate(finger):
				if note in chord:
					return i
			return None
		
		span = self._spans[position]
		return list(fingering(finger) for finger in span)

	def flight_time(self, prev_pos: Position, next_pos: Position):
		from_steps = self.calculate_steps(prev_pos)
		to_steps   = self.calculate_steps(next_pos)
		return self._flight_time(to_steps, from_steps)

