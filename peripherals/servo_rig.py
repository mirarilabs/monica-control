from . import Rig, Stepper, Button, FuzzyEncoder
import uasyncio
from machine import Timer


# A servo rig manages a stepper motor and its associated limit switches and encoder, with a servo-like movement profile
# Will cancel its instructions if a limit switch is pressed or gets out of sync with the encoder
# Will always home towards the lower limit switch
class ServoRig(Rig):
	def __init__(self, stepper: Stepper, lower_LS: Button, upper_LS: Button, encoder: FuzzyEncoder,
			homing_max_track: float, homing_prudent_track: float, homing_vel: int, homing_margin: float, homing_reengage_ms: int,
			stepper_2_encoder: float, encoder_update_ms: int):
		super().__init__()
		
		self._stepper = stepper
		self._lower_LS = lower_LS
		self._upper_LS = upper_LS
		self._encoder = encoder
		self.register_components(stepper, encoder, lower_LS, upper_LS)
		self._stepper._register_events("StartedHoming", "Homed", "SensorCancel")

		self._homing_max_track = homing_max_track
		self._homing_prudent_track = homing_prudent_track
		self._homing_vel = homing_vel
		self._homing_margin = homing_margin
		self._homing_reengage_ms = homing_reengage_ms
		self._stepper_2_encoder = stepper_2_encoder
		self._encoder_update_ms = encoder_update_ms

		self._encoder_timer = Timer(-1)
	
	@property
	def expected_encoder(self) -> float:
		return self._stepper_2_encoder * self._stepper.aprox_position

	def _encoder_cancel(self):
		print("Encoder cancel")
		self._sensor_cancel()
		# No longer homes automatically, but will cancel the current operation. Old code:
		# # Choose a safe fast track by using the minimum position reported by the stepper and the encoder, and then making it shorter
		# track = min(self._stepper.aprox_position, self._encoder.counter / self._stepper_2_encoder)
		# track -= self._homing_prudent_track
		# track = None if track <= 0 else track
		# self.go_home(track)
	
	def _lower_limit_cancel(self):
		print("Lower limit cancel")
		self._sensor_cancel()
		# No longer homes automatically, but will cancel the current operation. Old code:
		# self.go_home(None)
	
	def _upper_limit_cancel(self):
		print("Upper limit cancel")
		self._sensor_cancel()
		# No longer homes automatically, but will cancel the current operation. Old code:
		# self.go_home(self._homing_max_track)
	
	def _sensor_cancel(self):
		self._stepper.disengage()
		self._callbacks_off()
		self._stepper._trigger("SensorCancel")

	def go_home(self, fast_track: float | None = None):
		self._stepper.disengage()
		self._callbacks_off()
		print(f"Homing: fast_track: {fast_track}")
		uasyncio.create_task(self._homing_coro(fast_track))

	# TODO: should accept a position estimation and handle all homing alternatives
	# And use a fast track and slow landing, and you can tell it how much fast track you want
	async def _homing_coro(self, fast_track: float | None):
		self._stepper._trigger("StartedHoming")

		await uasyncio.sleep_ms(self._homing_reengage_ms)
		self._stepper._engage()
		home = self._lower_LS
		
		if fast_track is not None:
			if fast_track > 0:
				self._stepper.declare_position(fast_track)
				self._stepper.set_target(0)
				await self._stepper.wait("ReachedTarget")
			else:
				raise ValueError("Fast track must be positive or None")

		if not home.is_stable:
			await home.wait("Stable")
		
		if not home.is_pressed:
			self._stepper._set_velocity(-self._homing_vel)
			await home.wait("StablePress")
		
		self._stepper._set_velocity(self._homing_vel)
		await home.wait("StableRelease")
		self._stepper._set_velocity(0)

		self._stepper.declare_position(-self._homing_margin)
		self._stepper.set_target(0)
		await self._stepper.wait("ReachedTarget")
		
		self.encoder_sync()
		self._stepper._trigger("Homed")
		self._callbacks_on()

	def _callbacks_on(self):
		self._lower_LS.register_callback("Interrupt", self._lower_limit_cancel)
		self._upper_LS.register_callback("Interrupt", self._upper_limit_cancel)
		self._encoder_timer.init(mode=Timer.PERIODIC, period=self._encoder_update_ms, callback=self._encoder_update)
		self._stepper.register_callback("ReachedTarget", self.encoder_sync, True)

	def _callbacks_off(self):
		self._lower_LS.unregister_callback("Interrupt", self._lower_limit_cancel, strict=False)
		self._upper_LS.unregister_callback("Interrupt", self._upper_limit_cancel, strict=False)
		self._encoder_timer.deinit()
		self._stepper.unregister_callback("ReachedTarget", self.encoder_sync, True, strict=False)
	
	def encoder_sync(self):
		self._encoder.reset_counter(int(self.expected_encoder))

	def _encoder_update(self, _):
		expected_encoder = self.expected_encoder
		if not self._encoder.is_within_tolerance(expected_encoder):
			print(f"Encoder out of sync: Expected counter: {expected_encoder}, Counter: {self._encoder.counter}, Tolerance: {self._encoder.tolerance}, Uncertain updates: {self._encoder._uncertain_updates}")
			self._encoder_cancel()
	
	def __del__(self):
		print("Deleting ServoRig")
		self._callbacks_off()

