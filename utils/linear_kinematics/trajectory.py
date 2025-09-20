from utils.linear_kinematics.node import Node

# A trajectory is composed by a final state (with no acceleration) and a path of Nodes, whose lifespan lasts until the next one
# This is built through piece-wise constant acceleration instructions, so velocity is piece-wise linear and continuous, and position piece-wise quadratic and C^1
class Trajectory:
	# path should be consistent both internally and with the final state. If in doubt, create a path-less trajectory and extend() from there
	def __init__(self, time: float, pos: float, vel: float, path: list[Node] | None = None):
		self._time = time
		self._pos = pos
		self._vel = vel
		self._path = [] if path is None else path
	
	@property
	def time(self) -> float:
		return self._time
	
	@property
	def start(self) -> float:
		return self._path[0].time if self._path else self._time

	@property
	def final_state(self) -> Node:
		return Node(self._time, self._pos, self._vel, 0)

	def mirrored_copy(self) -> 'Trajectory':
		m_path = [n.mirrored_copy() for n in self._path]
		return Trajectory(self._time, -self._pos, -self._vel, m_path)

	def extend(self, duration: float, acceleration: float = 0.0):
		if not duration > 0:
			raise ValueError("Duration should be positive")
		
		self._path.append(Node(self._time, self._pos, self._vel, acceleration))
		self._time += duration
		self._pos += duration * self._vel + (acceleration * duration ** 2)/2
		self._vel += duration * acceleration

	def sample(self, t: float) -> Node:
		if t >= self._time:
			base = self.final_state
		else:
			base = None
			for n in self._path:
				if n.time <= t:
					base = n
				else:
					break
			if base is None:
				raise ValueError(f"Sampling time {t} is before the start of trajectory {self}")
		
		return base.extrapolate(t)

	def __bool__(self) -> bool:
		return True

	def __len__(self) -> int:
		return len(self._path)

	def __getitem__(self, index: int) -> Node:
		return self._path[index]

	def __iter__(self):
		return iter(self._path)

	def __str__(self) -> str:
		return f"Trajectory has {len(self)} path nodes: {', '.join(str(n) for n in self._path)} and currently at {self.final_state}"
	
	def __repr__(self) -> str:
		return self.__str__()

