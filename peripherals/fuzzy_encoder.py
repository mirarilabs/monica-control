from . import RotaryEncoder

# FuzzyEncoder is a wrapper around RotaryEncoder that adds a tolerance to the counter
# We can use uncertain updates as a proxy for overshooting errors (eg, when 3 counters are interpreted as -1, 4 as 0, 5 as 1, etc)
# Each overshooting error will generally add an error of 4 quadrant counters (a whole click)
# base_tolerance is the tolerance when there are no uncertain updates
# uncertain_tolerance is the extra tolerance per uncertain update
# It stands to reason that base_tolerance should be at least 2, as errors of 1 quadrant are common,
# and uncertain_tolerance should be at least 2, as each uncertain update adds at least 2 quadrant counters in an unknown direction
# Using 6 and 6 would allow for a free click (4 counters) error and assume another click error for every uncertain updates
# error = 1 (inherit resolution error) + 1 (timing tolerance) + 2 * uncertain_updates + 4 * overshooting_errors
class FuzzyEncoder(RotaryEncoder):
	def __init__(self, rotary_encoder_config: dict, base_tolerance: float, uncertain_tolerance: float):
		super().__init__(**rotary_encoder_config)
		
		self._base_tolerance = base_tolerance
		self._uncertain_tolerance = uncertain_tolerance
	
	@property
	def tolerance(self) -> float:
		return self._base_tolerance + self._uncertain_updates * self._uncertain_tolerance
	
	@property
	def lower_bound(self) -> float:
		return self.counter - self.tolerance
	
	@property
	def upper_bound(self) -> float:
		return self.counter + self.tolerance

	def is_within_tolerance(self, value: float) -> bool:
		return abs(value - self.counter) <= self.tolerance
	
	def debug(self):
		print(f"{type(self).__name__}: quadrant: {self._get_quadrant()}, X: {self._pin_x.value()}, Y: {self._pin_y.value()}"
			+ f", counter: {self._counter}, clicks: {self.get_clicks()}, uncertain: {self._uncertain_updates}"
			+ (f", turns: {self.get_turns()}" if self._clicks_per_turn is not None else "")
			+ f", tolerance: {self.tolerance}"
		)

