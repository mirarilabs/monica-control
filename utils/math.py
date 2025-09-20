import math


inf = math.inf

def sign(r: float) -> float:
	return -1 if r < 0 else 0 if r == 0 else 1

def length(x: float, y: float) -> float:
	return math.sqrt(x*x + y*y)

