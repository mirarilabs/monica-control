from utils.linear_kinematics.ik_agent import IKAgent, Trajectory
from math import sqrt, inf


# Linear IK model in which a typical trajectory will consist of constant acceleration, cruising and constant deceleration
# If initial velocity is greater than cruise_speed, a "return to bounds" segment will be added.
# Similarly so for a final "escape from bounds" to reach a greater speed
class SimpleAgent(IKAgent):
	def __init__(self, cruise_speed : float, accel : float) -> None:
		super().__init__()

		if not cruise_speed > 0:
			raise ValueError("cruise_speed should be a positive number")
		if not accel > 0:
			raise ValueError("accel should be a positive number")
		
		self._cruise_speed = cruise_speed
		self._accel = accel
	
	def __str__(self) -> str:
		return f"Simple Linear IK Agent: cruise_speed: {self._cruise_speed}, accel: {self._accel}"
	
	def __repr__(self) -> str:
		return self.__str__()

	# Minimizes duration given a target speed and acceleration.
	# Expected to always be feasible, and should investigate if unfeasibility conditions are found.
	def calculate_trajectory(self, p0: float, p1: float, v0: float, v1: float) -> Trajectory:
		
		prim = self._accel_then_decel( p0,  p1,  v0,  v1)
		dual = self._accel_then_decel(-p0, -p1, -v0, -v1)
		dual = dual.mirrored_copy() if dual else None

		prim_time = prim.time if prim else inf
		dual_time = dual.time if dual else inf

		t = prim if prim_time < dual_time else dual

		if t is None:
			raise RuntimeError(f"IMPORTANT! Unfeasible trajectory found for:" +
				f"p0: {p0}, p1: {p1}, v0: {v0}, v1: {v1}, cruise_speed: {self._cruise_speed}, accel: {self._accel}")
		
		return t

	# Minimizes duration by accelerating and the decelerating. Unfeasibility should be expected.
	def _accel_then_decel(self, p0: float, p1: float, v0: float, v1: float) -> Trajectory | None:
		M = self._cruise_speed
		A = self._accel
		
		# Initial segment: return to bounds
		a = 0
		if v0 > M:
			a = (v0 - M)/A
			p0 += a * (v0 + M)/2
			v0 = M

		# Final segment: escape from bounds
		e = 0
		if v1 > M:
			e = (v1 - M)/A
			p1 -= e * (M + v1)/2
			v1 = M

		H = A * (p1 - p0) + (v0**2 + v1**2)/2

		if H < 0:
			return None

		if H <= M**2:
			vm = sqrt(H)
			c = 0
		else:
			vm = M
			c = (H - M**2)/(A * M)

		b = (vm - v0)/A
		d = (vm - v1)/A

		if b < 0 or d < 0:
			return None
		
		trajectory = Trajectory(0, p0, v0)
		if a > 0: trajectory.extend(a, -A)
		if b > 0: trajectory.extend(b,  A)
		if c > 0: trajectory.extend(c)
		if d > 0: trajectory.extend(d, -A)
		if e > 0: trajectory.extend(e,  A)
		return trajectory

