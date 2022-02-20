import functools

from .parser import StringStream	

def read_input_as_streams(checker):
	"""
	Takes in a checker function that works with StreamParsers, and 
	makes them work with strings, as Program.stress_test expects.
	"""
	@functools.wraps(checker)
	def streamified(inp, correct, out):
		inp = StringStream(inp)
		correct = StringStream(correct)
		out = StringStream(out)
		try:
			return checker(inp, correct, out)
		except StreamParseError:
			return 0.0
	return streamified

@read_input_as_streams
def token_checker(inp, correct, out):
	while True:
		correct_token, output_token = correct.next_token(), out.next_token()
		if not correct_token and not output_token:
			return 1.0
		elif correct_token and output_token:
			if correct_token != output_token:
				return 0.0
		else:
			return 0.0
