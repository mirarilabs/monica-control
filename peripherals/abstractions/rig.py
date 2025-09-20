from .peripheral import Peripheral
from utils.iterables import iterable_arguments


class Rig:
	def __init__(self):
		if type(self) is Rig:
			raise TypeError("Rig cannot be instantiated directly")
		
		self._components: list[Peripheral] = []

	def register_components(self, *components):
		for c in iterable_arguments(components):
			self._components.append(c)

	def debug_components(self):
		print(f"Debugging {type(self).__name__} components")
		for p in self._components:
			p.debug()

	def reset_components(self):
		# print(f"Resetting {type(self).__name__} components")
		for p in self._components:
			p.reset()

