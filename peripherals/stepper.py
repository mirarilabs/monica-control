from . import EventfulPeripheral
from utils.linear_kinematics.simple_agent import SimpleAgent
from machine import Pin, PWM
from time import ticks_ms, ticks_add
from math import trunc
from utils.time import elapsed
from machine import Timer


MAX_DUTY = 32768

MODE_SETTINGS = {
	 1: (0, 0, 0),
	 2: (1, 0, 0),
	 4: (0, 1, 0),
	 8: (1, 1, 0),
	16: (0, 0, 1),
	32: (1, 0, 1)
}

class Stepper(EventfulPeripheral):
	def __init__(self, pin_mode0: int, pin_mode1: int, pin_mode2: int, stepping_mode: int, pin_engage: int, pin_dir: int, pin_step: int,
			dir_0_is_positive: bool, cruise_speed : float, accel : float, interval_ms: int, pwm_duty: int = MAX_DUTY):
		super().__init__()

		self._pin_mode0 = Pin(pin_mode0, Pin.OUT)
		self._pin_mode1 = Pin(pin_mode1, Pin.OUT)
		self._pin_mode2 = Pin(pin_mode2, Pin.OUT)
		m_s = MODE_SETTINGS[stepping_mode]
		self._pin_mode0(m_s[0])
		self._pin_mode1(m_s[1])
		self._pin_mode2(m_s[2])

		self._pin_engage = Pin(pin_engage, Pin.OUT)
		self._pin_dir = Pin(pin_dir, Pin.OUT)
		self._pin_step = Pin(pin_step, Pin.OUT)
		self._pwm = PWM(self._pin_step)
		self._pwm_duty = pwm_duty

		self._dir_0_is_positive = dir_0_is_positive
		self._ik_agent = SimpleAgent(cruise_speed, accel)

		self.declare_position(0)
		self._register_events("Engaged", "Disengaged", "ReachedTarget")
		self.disengage()

		self._interval_ms = interval_ms
		self._timer = Timer() # type: ignore
		self._timer.init(period=interval_ms, callback=self.update)


	@property
	def is_engaged(self) -> int:
		return not self._pin_engage.value()

	@property
	def velocity(self) -> int:
		return self._velocity

	@property
	def direction(self) -> int:
		return -1 if self._velocity < 0 else 0 if self._velocity == 0 else 1

	@property
	def target(self) -> float | None:
		return self._target

	@property
	def ETA(self) -> float | None:
		if self._target is None:
			return None
		else:
			assert self._trajectory is not None and self._trajectory_start_ms is not None
			return self._trajectory.time - elapsed(self._trajectory_start_ms, ticks_ms())
	
	@property
	def aprox_position(self) -> float:
		return self._position + elapsed(self._position_ms, ticks_ms()) * self._velocity

	def declare_position(self, pos: float):
		self._position = pos
		self._position_ms = ticks_ms()
	
	def _update_position(self):
		now_ms = ticks_ms()
		self._position += elapsed(self._position_ms, now_ms) * self._velocity
		self._position_ms = now_ms

	def _set_velocity(self, vel: int):
		self._velocity = vel
		if vel == 0:
			self._pwm.duty_u16(0)
		else:
			dir = (vel < 0) == self._dir_0_is_positive
			self._pin_dir(dir)
			self._pwm.duty_u16(self._pwm_duty)
			self._pwm.freq(abs(vel))
	
	def _clear_target(self):
		assert self._velocity == 0, f"Trying to clear target while velocity is non-zero: {self._velocity}"
		self._target = None
		self._trajectory = None
		self._trajectory_start_ms = None
	
	def _engage(self):
		self._set_velocity(0)
		self._clear_target()
		self._pin_engage(0)
		self._trigger("Engaged")
	
	def disengage(self):
		self._pin_engage(1)
		self._set_velocity(0)
		self._clear_target()
		self._trigger("Disengaged")
	
	def set_target(self, target: float):
		# Set target to None to block race conditions against the Timer, who will just skip a cycle
		self._target = None
		if not self.is_engaged:
			self._engage()
		self._update_position()
		self._trajectory = self._ik_agent.calculate_trajectory(self._position, target, self._velocity, 0)
		self._trajectory_start_ms = self._position_ms
		self._target = target

	def update(self, timer):
		self._update_position()
		if self._target is not None:
			assert self._trajectory is not None and self._trajectory_start_ms is not None
			next_position_ms = ticks_add(self._position_ms, self._interval_ms)
			next_position_time = elapsed(self._trajectory_start_ms, next_position_ms)
			next_position = self._trajectory.sample(next_position_time).position
			vel = trunc((next_position - self._position) * 1000/self._interval_ms)
			if abs(vel) < 8:
				vel = 0
			self._set_velocity(vel)
		
			if abs(self._position - self._target) <= 0.5 and vel == 0:
				self.disengage()
				self._trigger("ReachedTarget")

	def debug(self):
		print(f"{type(self).__name__}: estimated position: {self.aprox_position}, target: {self._target}, velocity: {self._velocity}, ETA: {self.ETA}")

	def reset(self):
		super().reset()
		self._timer.deinit()
		self._pwm.deinit()
		self._pin_engage(1)
		self._pin_dir.init(Pin.IN)
		self._pin_step.init(Pin.IN)
		self._pin_mode0.init(Pin.IN)
		self._pin_mode1.init(Pin.IN)
		self._pin_mode2.init(Pin.IN)

