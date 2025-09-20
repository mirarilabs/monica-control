from . import Peripheral
import uasyncio
import math
from machine import Pin, PWM


MAX_DUTY = 32768

class Buzzer(Peripheral):
	def __init__(self, pin, general_volume = 1.0):
		super().__init__()
		self.pwm = PWM(Pin(pin))
		self.general_volume = general_volume
		self.silence()
	
	def reset(self):
		super().reset()
		self.silence()
	
	def silence(self):
		self.pwm.duty_u16(0)

	async def play_tone(self, frequency, duration, volume = 1.0):
		self.pwm.freq(frequency)
		self.pwm.duty_u16(math.floor(volume * self.general_volume * MAX_DUTY))
		await uasyncio.sleep(duration)
		self.silence()

	async def play_score(self, score, silenceLength, volume = 1.0):
		for note in score:
			await self.play_tone(note[0], note[1], volume)
			await uasyncio.sleep(silenceLength)

