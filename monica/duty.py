from utils.time import TimeMS
from utils.music.chord import Chord


# Skid represents a Position differential, the shift a wagon should do while pressing the keys to do a pitch shift,
# Probably a multiple of 7 (an octave in a keyboard, jumping 14 nullable keys)
Skid = int

# Duty represents a chord or silence that is to be play, and when, and how
class Duty:
	__slots__ = ['start_ms', 'duration_ms', 'chord', 'skid']

	def __init__(self, start_ms: TimeMS, duration_ms: TimeMS, chord: Chord | None, skid: Skid = 0):
		if duration_ms <= 0:
			raise ValueError(f"Invalid duration: {duration_ms}")

		self.start_ms = start_ms
		self.duration_ms = duration_ms
		self.chord = chord
		self.skid = skid
	
	@property
	def end_ms(self) -> TimeMS:
		return self.start_ms + self.duration_ms
	
	@property
	def is_silent(self) -> bool:
		return self.chord is None
	
	@classmethod
	def silence(cls, start_ms: TimeMS, duration_ms: TimeMS) -> 'Duty':
		return cls(start_ms, duration_ms, None)
	
	def __str__(self) -> str:
		return f"Duty(start: {self.start_ms}ms, end: {self.end_ms}ms, duration: {self.duration_ms}ms, chord: {self.chord}, skid: {self.skid} positions)"
	
	def __repr__(self) -> str:
		return self.__str__()

	@classmethod
	def fill_with_silence(cls, duties: list['Duty']) -> list['Duty']:
		sequence: list[Duty] = []
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

