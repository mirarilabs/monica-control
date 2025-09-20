from ..iterables import chain
import uasyncio
import config


# A wrapper for a uasyncio.Event object with added callback functionality
# so that the originator of the event needs not worry about its repercutions.
# Triggering it excecutes the onetime callbacks, then the peristent callbacks, and finally
# sets and clears the event (any code waiting on it will be woken up after the trigger method stops)
# Note: due to interpreter limitations, a keep_awake() task is created to keep the event loop awake.
# Waiting on events will only bring tragedy.
class EventBroadcast:
	def __init__(self):
		self._event = uasyncio.Event()
		self._callbacks_onetime = []
		self._callbacks_persist = []
	
	def clear_onetime_callbacks(self):
		self._callbacks_onetime.clear()
	
	def clear_persist_callbacks(self):
		self._callbacks_persist.clear()
	
	def clear_callbacks(self):
		self.clear_onetime_callbacks()
		self.clear_persist_callbacks()

	def register_callback(self, callback, persist=False):
		target_list = self._callbacks_persist if persist else self._callbacks_onetime
		target_list.append(callback)
	
	def unregister_callback(self, callback, persist=False, strict=True):
		target_list = self._callbacks_persist if persist else self._callbacks_onetime
		if callback not in target_list:
			if strict:
				raise ValueError(f"Callback not found in the {'persist' if persist else 'onetime'} list")
			else:
				return
		target_list.remove(callback)
	
	def trigger(self, *args, **kwargs):
		callbacks = self._callbacks_onetime + self._callbacks_persist
		for callback in callbacks:
			callback(*args, **kwargs)
		self.clear_onetime_callbacks()
		self._event.set()
		self._event.clear()
	
	def wait(self):
		return self._event.wait() #type: ignore


awake_interval_ms = config.events["awake_interval_ms"]

async def keep_awake():
	while True:
		await uasyncio.sleep_ms(awake_interval_ms)

uasyncio.create_task(keep_awake())

