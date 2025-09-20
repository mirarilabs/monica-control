from . import EventfulPeripheral
from machine import Pin, Timer


# A button with simple, stable signals, debounced by design.
# Regular polling provides context, while chaotic interrupts provide raw auxiliary data.
# The _interrupted flag signals that an interruption occured since the last sample, and value and diff will be forced to reflect that,
# even if polling didn't detect the value change, to mantain information integrity (so _last_sample and _value might differ)
# Use sample_now to access the raw data.
class Button(EventfulPeripheral):
	def __init__(self, pin, poll_interval_ms=50):
		super().__init__()
		self._pin = Pin(pin, Pin.IN, Pin.PULL_UP)
		self._poll_interval_ms = poll_interval_ms

		self._prev_sample = self.sample_now()
		self._value = self._prev_sample
		self._diff = 0
		self._stable = True
		self._interrupted = False

		self._register_events("Press", "Release", "Interrupt", "Stable", "StablePress", "StableRelease")
		self._timer = Timer(-1)
		self._timer.init(mode=Timer.PERIODIC, period=poll_interval_ms, callback=self._poll)
		self._pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._handler)
	
	def sample_now(self) -> int:
		return self._pin.value()
	
	@property
	def value(self) -> int:
		return self._value
	
	@property
	def diff(self) -> int:
		return self._diff
	
	@property
	def is_pressed(self) -> bool:
		return self._value == 1
	
	@property
	def is_stable(self) -> bool:
		return self._stable

	def _poll(self, _):
		sample = self.sample_now()
		keep_value = (sample == self._prev_sample) and (sample == self._value) and not self._interrupted

		if keep_value:
			self._diff = 0
			if not self._stable:
				self._stable = True
				self._trigger("Stable")
				if self._value:
					self._trigger("StablePress")
				else:
					self._trigger("StableRelease")
		elif self._value == 0:
			self._value = 1
			self._diff = 1
			self._trigger("Press")
		else:
			self._value = 0
			self._diff = -1
			self._trigger("Release")

		self._prev_sample = sample
		self._interrupted = False
	
	def _handler(self, _):
		if self._interrupted:
			return
		
		self._interrupted = True
		self._stable = False
		self._trigger("Interrupt")
	
	def debug(self):
		print(f"{type(self).__name__}: value: {self.value}, diff: {self.diff}")
	
	def reset(self):
		self._timer.deinit()

