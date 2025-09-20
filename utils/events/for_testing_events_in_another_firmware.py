import uasyncio
from machine import Pin, Timer


# Update: Maybe when events are properly supported use this script to test them
# After writing the explanation below I found out that when a task waits for an event,
# it somehow stops getting the sleeps right until something else wakes it up, so I
# ended up using a keep_awake() with short sleeps, but not flush because it's unstable

# Old explanation:
# Try updating the firmware to see if either of these can be removed
# (compare each version of the code in two devices with different firmware)
# Creating the keep_alive task is needed so that waiting for just an event doesn't terminate
# Running a dummy task after triggering the event is needed to flush the event loop
# As it's set up, keep_alive naturally does a slow flush every 5 seconds, so that helps
# test if the flush task is needed. The event print would either take too long or nothing at all,
# so one would see either a single event every 5 seconds or every 1 second
# (on top of that, the pin events don't realize until the flush either)
# As of today's firmware, if USE_KEEP_ALIVE is disabled the program terminates without warning,
# and if RUN_FLUSH_TASK is disabled the event print doesn't happen until something else wakes up
# the event loop, so neither can be disabled
# See my comment: https://github.com/micropython/micropython/pull/15302#issuecomment-2545730794

USE_KEEP_ALIVE = True
RUN_FLUSH_TASK = True

async def keep_alive():
	while True:
		await uasyncio.sleep_ms(5000)

async def flush_task():
	pass

flush_coro = flush_task()


def trigger(_=None):
	event.set()
	event.clear()
	if RUN_FLUSH_TASK:
		uasyncio.run(flush_coro)

async def wait_for_event():
	while True:
		await event.wait() #type: ignore
		print("event")


# Set up both pin and timer interrupts to trigger the event
Pin(0, Pin.IN, Pin.PULL_UP).irq(trigger)
Timer(-1).init(mode=Timer.PERIODIC, period=1000, callback=trigger)

event = uasyncio.Event()
if USE_KEEP_ALIVE:
	uasyncio.create_task(keep_alive())
uasyncio.run(wait_for_event())

