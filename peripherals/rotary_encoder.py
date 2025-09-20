from . import Peripheral
from machine import Pin


# This rotary encoder ignores the usual switch button
# If present, it should be treated as a regular button on an unrelated pin
# The traditionally called CLK and DT pins will be called X and Y.

# We have the four points in the plane:
# (calling them Quadrants is a manner of speaking)
# Quadrant | (X, Y)
#		0 | (0, 0)
#		1 | (1, 0)
#		2 | (1, 1)
#		3 | (0, 1)
# Quadrant changes are counted
# A click is made of 4 counter units
# A turn is made of clicks_per_turn clicks
# Clicks are discretized, while turns are though as a continuum

class RotaryEncoder(Peripheral):
	def __init__(self, pin_x: int, pin_y: int, clicks_per_turn: int, clockwise: bool, default_to_last_diff: bool):
		super().__init__()
		
		self._pin_x = Pin(pin_x, Pin.IN, Pin.PULL_UP)
		self._pin_y = Pin(pin_y, Pin.IN, Pin.PULL_UP)
		self._clicks_per_turn = clicks_per_turn
		self._direction = -1 if clockwise else 1
		self._default_to_last_diff = default_to_last_diff

		self.reset_counter(0)
	
	@property
	def counter(self) -> int:
		return self._counter
	
	@property
	def unresolved_updates(self) -> int:
		return self._uncertain_updates
	
	def reset_unresolved_updates(self):
		self._uncertain_updates = 0

	def _get_quadrant(self) -> int:
		x = self._pin_x.value()
		y = self._pin_y.value()
		return 2 * x + x ^ y # X is the second digit, and the first is (X xor Y)
	
	def _callbacks_on(self):
		self._pin_x.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._update)
		self._pin_y.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._update)
	
	def _callbacks_off(self):
		self._pin_x.irq(None)
		self._pin_y.irq(None)
	
	def reset_counter(self, initial_counter: int):
		self._callbacks_off()
		self._last_quadrant = self._get_quadrant()
		self._last_diff = 0
		self._counter = initial_counter
		self.reset_unresolved_updates()
		self._callbacks_on()

	def get_clicks(self) -> int:
		return self._counter // 4

	def get_turns(self) -> float:
		return self._counter / (4 * self._clicks_per_turn)

	def _update(self, _):
		quadrant = self._get_quadrant()
		diff = (quadrant - self._last_quadrant) % 4

		if diff == 0:
			return
		elif diff == 1:
			self._counter += self._direction
			self._last_diff = diff
		elif diff == 3:
			self._counter -= self._direction
			self._last_diff = diff
		else:
			self._uncertain_updates += 1
			if self._default_to_last_diff:
				dir = self._direction if self._last_diff == 1 else -self._direction if self._last_diff == 3 else 0
				self._counter += 2 * dir
		
		self._last_quadrant = quadrant
	
	def debug(self):
		print(f"{type(self).__name__}: quadrant: {self._get_quadrant()}, X: {self._pin_x.value()}, Y: {self._pin_y.value()}"
			+ f", counter: {self._counter}, clicks: {self.get_clicks()}, unresolved: {self._uncertain_updates}"
			+ (f", turns: {self.get_turns()}" if self._clicks_per_turn is not None else "")
		)

	def reset(self):
		super().reset()
		self._callbacks_off()

