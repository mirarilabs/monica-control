

def is_iterable(obj):
	try:
		iter(obj)
		return True
	except TypeError:
		return False

def iterable_arguments(args: tuple):
	return args[0] if len(args) == 1 and not isinstance(args[0], str) and is_iterable(args[0]) else args

def chain(*iterables):
	for iter in iterables:
		yield from iter

def remove_None_iterable(obj		): return		(i for i in obj if i is not None)
def remove_None_set		(obj: set	): return set	(i for i in obj if i is not None)
def remove_None_list	(obj: list	): return list	(i for i in obj if i is not None)
def remove_None_tuple	(obj: tuple	): return tuple	(i for i in obj if i is not None)

def union(sets) -> set:
	u = set()
	for s in sets:
		u.update(s)
	return u

