from machine import Pin
import uasyncio
from utils.iterables import iterable_arguments


# At some point the pin default settings should be more easily configurable

ALL_INDICES = range(30)
DEFAULT_PINS = ALL_INDICES

# Create all pins anyways so as to keep indexing neat
_pins = [Pin(i, Pin.IN, Pin.PULL_DOWN) for i in ALL_INDICES]
_interval = 1.0

def pressed(i):
	return _pins[i].value()

def set_interval(new_interval):
	global _interval
	_interval = new_interval

def debug_pins(*selected):
	selected = iterable_arguments(selected)
	pins = DEFAULT_PINS if not selected else selected
	values_iter = (f"{i}: {'On ' if pressed(i) else 'Off'}" for i in pins)
	print("Pin values: " + ", ".join(values_iter))

async def auto_debug_pins():
	tracked = [False for i in ALL_INDICES]
	while True:
		for i in ALL_INDICES:
			if pressed(i):
				tracked[i] = True
		debug_pins(i for i in ALL_INDICES if tracked[i])
		await uasyncio.sleep(_interval)

def start_auto_debug_task():
	coro = auto_debug_pins()
	return uasyncio.create_task(coro)

