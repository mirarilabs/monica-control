from . import EventfulPeripheral
from machine import Pin, PWM
import uasyncio


# TODO: Explain better
# This is a servo that is expected to move on its own to a target position, and roughly estimate its positiona at any time
# min_duty and max_duty should be the servos' physical limits set by the manufacturer, so you never change them
# Actual operational range of positions should be enforced by code (or eventually, through a position_aliases system)
# flight_time should be how much time it takes to move from min_duty to max_duty
# From that, it does a simple estimation of position from its known physical speed, which is as reliable as life itself
# so it's better to err on the slow side and set a flight_time that is a bit longer than the actual time
# The first flight is blind so it might set the homing event a bit late
# Homing triggers an special event, that is not the same as simple setting the target to the home position
# Eventually, implement a trajectory system for the servos, so they can follow a curve to the target position
# If not provided, the named position "Home" will be set to 0
class StandardServo(EventfulPeripheral):
	def __init__(self, pin: int, min_duty: int, max_duty: int, max_flight_time: float, pwm_freq: int, named_positions: dict[str, float] | None = None):
		super().__init__()
		self._pin = Pin(pin, Pin.OUT)
		self._pwm = PWM(self._pin)
		self._pwm.freq(pwm_freq)
		
		self._min_duty = min_duty
		self._max_duty = max_duty
		self._max_flight_time = max_flight_time
		self._named_positions = named_positions if named_positions is not None else {}
		if "Home" not in self._named_positions:
			raise ValueError("Named positions must include 'Home' position")

		self._idle_position = None
		self._moving_task = None

		self._register_events("ReachedHome", "ReachedTarget")
	
	@property
	def is_idle(self):
		return self._idle_position is not None
	
	@property
	def is_moving(self):
		return self._moving_task is not None
	
	@property
	def is_uncertain(self):
		return not self.is_idle and not self.is_moving
	
	@property
	def position(self):
		if not self.is_idle:
			raise NotImplementedError("Position estimation during movement not implemented")
		return self._idle_position
	
	@property
	def is_engaged(self):
		return self._pwm.duty_u16() != 0
	
	def _engage(self, duty):
		self._pwm.duty_u16(duty)
	
	def _disingage(self):
		self._pwm.duty_u16(0)

	def cancel_movement(self):
		if not self.is_moving:
			raise ValueError("Trying to cancel non-existing movement")
		# The servo is left in uncertain state, as it was moving and had no idle_position
		self._moving_task.cancel() #type: ignore
		self._moving_task = None
		self._disingage()
	
	def go_home(self):
		if self.is_moving:
			self.cancel_movement()
		self._idle_position = None
		self._start_movement("Home")
	
	def go_to(self, target: str | float | int):
		if self.is_uncertain:
			raise ValueError("Servo in uncertain state, needs homing first")
		
		if self.is_moving:
			print("Servo is already moving, cancelling current movement")
			self.cancel_movement()
		
		self._start_movement(target)
	
	def go_to_percent(self, percent: int | float):
		"""Go to position specified as percentage (0-100%) with volume rescaling"""
		if not 0 <= percent <= 100:
			raise ValueError("Percentage must be between 0 and 100")
		
		# Apply volume rescaling: 0-100% user input maps to 20-60% servo range
		target = self._map_volume_percentage(percent)
		self.go_to(target)
	
	def _map_volume_percentage(self, user_percent: float) -> float:
		"""
		Map user volume percentage to actual servo position
		- User 0% → Servo 0% (silence)
		- User 100% → Servo 60% (practical maximum)
		- Maps 0-100% user input to 20-60% servo range
		"""
		if user_percent <= 0:
			return 0.0  # Silence
		
		# Map 0-100% user input to 20-60% servo range
		# Formula: servo_percent = 20 + (user_percent * 40 / 100)
		servo_percent = 20 + (user_percent * 40 / 100)
		
		# Convert to 0-1 range for servo
		return servo_percent / 100.0
	
	def _start_movement(self, target: float | str | int):
		event = "ReachedHome" if target == "Home" else "ReachedTarget"

		if isinstance(target, str):
			if target not in self._named_positions:
				raise ValueError(f"Target position {target} not found in named positions")
			target = self._named_positions[target]
		elif isinstance(target, int):
			# Handle percentage input (0-100) with volume rescaling
			if not 0 <= target <= 100:
				raise ValueError("Percentage must be between 0 and 100")
			target = self._map_volume_percentage(target)
		elif not 0 <= target <= 1:
			raise ValueError("Target position must be between 0 and 1")
		
		self._moving_task = uasyncio.create_task(self._movement_coro(target, event))

	async def _movement_coro(self, target: float, event: str):
		origin = self._idle_position
		self._idle_position = None

		target_duty = int((1 - target) * self._min_duty + target * self._max_duty)
		flight_portion = 1 if origin is None else abs(target - origin)
		duration = self._max_flight_time * flight_portion

		self._engage(target_duty)
		await uasyncio.sleep(duration)
		self._disingage()
		self._idle_position = target
		self._moving_task = None

		self._trigger(event)

	def reset(self):
		super().reset()
		self._disingage()
		if self.is_moving:
			self.cancel_movement()
		self._idle_position = None
		self._pwm.deinit()
	
	def debug(self):
		print(f"{type(self).__name__}: engaged: {self.is_engaged}, idle position: {self._idle_position}")

