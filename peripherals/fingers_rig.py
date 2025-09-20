from peripherals import Rig, StandardServo
import uasyncio


FINGERING_TARGETS = {
	0: "Left",
	1: "Right",
	None: "Home"
}

class FingersRig(Rig):
	def __init__(self, fingers: list[StandardServo], move_wait_ms: int):
		super().__init__()
		self._fingers = fingers
		self._move_wait_ms = move_wait_ms
		self.register_components(fingers)
	
	def go_home(self):
		for finger in self._fingers:
			finger.go_home()

	def cancel_movement(self):
		for finger in self._fingers:
			if finger.is_moving:
				finger.cancel_movement()
	
	def play(self, fingerings: list):
		for finger, fingering in zip(self._fingers, fingerings):
			finger.go_to(FINGERING_TARGETS[fingering])
	
	async def cautionary_wait(self):
		await uasyncio.sleep_ms(self._move_wait_ms)

