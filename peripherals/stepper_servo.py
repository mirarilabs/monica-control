from . import Stepper, Button, RotaryEncoder


# TODO: Pasar acá el codigo de servo rig

# A stepper servo is a stepper motor and its associated limit switches and encoder, with a servo-like movement profile
# Will cancel its instructions and initiate a homing procedure if a limit switch is pressed or gets out of sync with the encoder
class StepperServo(Stepper):
	def __init__(self, stepper_config: dict, lower_LS: Button, upper_LS: Button, encoder: RotaryEncoder, sync_tolerance: float):
		super().__init__(**stepper_config)

		self._lower_LS = lower_LS
		self._upper_LS = upper_LS
		self._encoder = encoder
		self._sync_tolerance = sync_tolerance

		self._lower_LS.register_callback("Interrupt", self._lower_LS_handler)
		self._upper_LS.register_callback("Interrupt", self._upper_LS_handler)

	def _lower_LS_handler(self):
		self.disengage()
		print("Lower limit switch pressed")

	def _upper_LS_handler(self):
		self.disengage()
		print("Upper limit switch pressed")

