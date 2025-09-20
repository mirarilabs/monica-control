

# Nodes are points in time in phase space
class Node:
	__slots__ = ['time', 'position', 'velocity', 'acceleration']

	def __init__(self, time: float, position: float, velocity: float, acceleration: float):
		self.time = time
		self.position = position
		self.velocity = velocity
		self.acceleration = acceleration

	def mirrored_copy(self):
		return Node(self.time, -self.position, -self.velocity, -self.acceleration)
	
	def extrapolate(self, t: float):
		dt = t - self.time
		vel_ex = self.velocity + dt * self.acceleration
		pos_ex = self.position + dt * (self.velocity + vel_ex)/2

		return Node(t, pos_ex, vel_ex, self.acceleration)

	def __str__(self) -> str:
		return f"Node(time: {self.time:.2f}, pos: {self.position:.2f}, vel: {self.velocity:.2f}, acc: {self.acceleration:.2f})"
	
	def __repr__(self) -> str:
		return self.__str__()

