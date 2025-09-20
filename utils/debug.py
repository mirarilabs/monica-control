import gc


def memory(marker_name = None):
	allo = str(gc.mem_alloc())
	free = str(gc.mem_free ())
	allo = allo[:-3] + " " + allo[-3:]
	free = free[:-3] + " " + free[-3:]
	print(f"Allocated memory{ ' at ' + str(marker_name) if marker_name else ''}: {allo} bytes, free memory: {free} bytes")

