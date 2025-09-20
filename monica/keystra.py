from monica.duty import Duty, TimeMS, Skid
from monica.wagon import Wagon, Position, Quality
from utils.math import *


# Choice represents an edge in the pathfinding, that is where it came from and the accumulated quality
class Choice:
	__slots__ = ['position', 'quality']

	def __init__(self, position: Position, quality: Quality):
		self.position = position
		self.quality = quality

	def __str__(self) -> str:
		return f"({self.position}, {math.floor(self.quality)})"
	
	def __repr__(self) -> str:
		return self.__str__()

# Keystra turns a keyboard into a fun optimization problem
class Keystra:
	def __init__(self, wagon: Wagon, notes_bonus: float, skid_bonus: float, move_penalty: float, time_penalty: float):
		self._wagon = wagon
		self._positions = wagon.valid_positions
		self._silence_quality : list[Quality] = [0.0] * self._positions

		self._notes_bonus  = notes_bonus
		self._skid_bonus   = skid_bonus
		self._move_penalty = move_penalty
		self._time_penalty = time_penalty

	def choice_quality(self, prev_time_ms: TimeMS, next_time_ms: TimeMS, prev_pos: Position, next_pos: Position, covering_quality: Quality, skid : Skid) -> Quality:
		quality: Quality = 0

		# Bias towards balanced trajectories across time
		delta_time = (next_time_ms - prev_time_ms)/1000.
		delta_pos = next_pos - prev_pos
		quality -= length(self._move_penalty * delta_pos, self._time_penalty * delta_time)

		flight_time = self._wagon.flight_time(prev_pos, next_pos)
		if flight_time > delta_time:
			return -inf
		
		# If the skid is not valid, no key will be pressed if this path is chosen later on
		wanted_skid = delta_pos == skid
		no_skid = delta_pos == 0
		valid_skid = wanted_skid or no_skid
		if valid_skid and covering_quality > 0:
			quality += (delta_time + 1) * (self._notes_bonus * (covering_quality + 1) + wanted_skid * self._skid_bonus)
		
		return quality

	# Completes the given sequence with silences, so Duties are back to back, then explores the optimal (but rough) chain of movements for the robot.
	# Returns the complete sequence and an associated list of positions (which is one longer)
	def fill_and_explore(self, duties: list[Duty]) -> tuple[list[Duty], list[Position]]:
		duties = Duty.fill_with_silence(duties)
		choices: list[list[Choice]] = [ [ Choice(-1, 0) ] * self._positions ]
		for duty in duties:
			next_choices: list[Choice] = list()
			covering_qualities: list[Quality] = self._wagon.covering_qualities(duty.chord) if duty.chord else self._silence_quality
			for next_pos in range(self._positions):
				max_path = -1
				max_quality = -inf
				for prev_pos in range(self._positions):
					choice_quality = self.choice_quality(duty.start_ms, duty.end_ms, prev_pos, next_pos, covering_qualities[prev_pos], duty.skid)
					path_quality = choices[-1][prev_pos].quality + choice_quality
					if path_quality > max_quality:
						max_path = prev_pos
						max_quality = path_quality
				next_choices.append(Choice(max_path, max_quality))
			choices.append(next_choices)

		# We start the backtrace at the final Choice with the highest Quality, and then work backwards from there
		path : list[Position] = [-1] * len(choices)
		path[-1] = max(range(self._positions), key=lambda pos: choices[-1][pos].quality)
		for i in range(len(choices) - 1, 0, -1):
			path[i - 1] = choices[i][path[i]].position

		return duties, path

