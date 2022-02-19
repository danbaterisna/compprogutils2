import functools, io

def generator(gen):
	"""
	Decorator for writing a generator.

	Accepts a generator function with a single parameter (a print function),
	and converts that function into one usable by Program's methods.
	"""
	@functools.wraps(gen)
	def with_printer():
		output = io.StringIO()
		def oprint(*args):
			print(*args, file=output)
		gen(oprint)
		return output.getvalue()
	return with_printer

