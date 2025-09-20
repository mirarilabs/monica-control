from .peripheral import Peripheral
from utils.events.event_broadcast import EventBroadcast
from utils.iterables import iterable_arguments


# A peripheral with an EventBroadcast dictionary and wrapper methods for ease of access
# __getitem__ was implemented as syntactic sugar for the events dictionary
class EventfulPeripheral(Peripheral):
	def __init__(self):
		if type(self) is EventfulPeripheral:
			raise TypeError("EventfulPeripheral cannot be instantiated directly")
		
		super().__init__()
		self._events: dict[str, EventBroadcast] = {}
	
	def _register_events(self, *events):
		events = iterable_arguments(events)
		conflicts = set(events) & set(self._events)
		if conflicts:
			raise ValueError(f"Events already registered: {conflicts}")
		
		self._events.update({e: EventBroadcast() for e in events})
	
	def __getitem__(self, event: str):
		return self._events[event]
	
	def clear_onetime_callbacks(self, event: str):
		self._events[event].clear_onetime_callbacks()
	
	def clear_persist_callbacks(self, event: str):
		self._events[event].clear_persist_callbacks()
	
	def clear_callbacks(self, event: str):
		self._events[event].clear_callbacks()
	
	def register_callback(self, event: str, callback, persist=False):
		if event not in self._events:
			raise ValueError(f"Event not registered: {event}. Available events: {self._events.keys()}")
		self._events[event].register_callback(callback, persist)
	
	def unregister_callback(self, event: str, callback, persist=False, strict=True):
		self._events[event].unregister_callback(callback, persist, strict)
	
	def _trigger(self, event: str, *args, **kwargs):
		self._events[event].trigger(*args, **kwargs)

	def wait(self, event: str):
		return self._events[event].wait()
	
	def reset(self):
		super().reset()
		self._events.clear()

