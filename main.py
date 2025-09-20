import device
import monica
import uasyncio


MAIN_CORO = monica.run()

try:
	uasyncio.run(MAIN_CORO)
except KeyboardInterrupt:
	MAIN_CORO.close()
finally:
	device.reset_peripherals()

