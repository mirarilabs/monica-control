import time

TimeMS = int

def elapsed(before: TimeMS, after: TimeMS) -> float:
	return time.ticks_diff(after, before)/1000

