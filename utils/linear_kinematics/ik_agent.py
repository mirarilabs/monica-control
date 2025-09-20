from utils.linear_kinematics.trajectory import Trajectory


# Agents store persistent configurations and resolve general IK problems in their own way
class IKAgent:
	def __init__(self) -> None:
		if type(self) is IKAgent:
			raise TypeError("IKAgent cannot be instantiated directly")
	
	# Solves a linear IK problem given initial/final positions/velocities
	def calculate_trajectory(self, p0: float, p1: float, v0: float, v1: float) -> Trajectory:
		raise NotImplementedError()

	# Outputs just the duration of a simplified IK problem given initial/final positions with naught initial/final velocities
	# Ideally overload with a more efficient custom implementation
	def flight_time(self, p0: float, p1: float) -> float:
		return self.calculate_trajectory(p0, p1, 0, 0).time

	def __str__(self) -> str:
		raise NotImplementedError(f"Please implement the string casting of this IKAgent: {type(self)}")
	
	def __repr__(self) -> str:
		return self.__str__()

