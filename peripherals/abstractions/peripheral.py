import uasyncio


__peripherals_list = []

def debug_peripherals():
	for p in __peripherals_list:
		p.debug()

def reset_peripherals():
	for p in __peripherals_list:
		p.reset()


class Peripheral:
	def __init__(self):
		if type(self) is Peripheral:
			raise TypeError("Peripheral cannot be instantiated directly")
		
		__peripherals_list.append(self)
	
	def debug(self):
		raise NotImplementedError(f"Please override peripheral debug for: {type(self).__name__}")
	
	async def _auto_debug_coroutine(self, period: float):
		while True:
			self.debug()
			await uasyncio.sleep(period)
	
	def start_auto_debug(self, period: float = 0.1):
		self._auto_debug_task = uasyncio.create_task(self._auto_debug_coroutine(period))
	
	def stop_auto_debug(self):
		if self._auto_debug_task is None:
			raise ValueError("Auto debug task is not running")
		
		self._auto_debug_task.cancel() #type: ignore
	
	def reset(self):
		# print(f"Resetting {type(self).__name__}")
		pass

