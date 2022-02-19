import collections, functools, string

class StreamParseError(Exception):
	""" Raised when one of the default StreamParsers raises an error. """
	pass

class StreamSource:
	""" A base class for sources for StreamParser input."""

class StringSource(StreamSource):

class ProgramSource(StreamSource):


class StreamParserChain:
	""" A helper class that facilitates the chaining of StreamParser methods. """
	def __init__(self, sp, precursor = None):
		self.sp = sp
		self.precursor = precursor
		self.parse_result = None
	
	def __iter__(self):
		if self.precursor: yield from self.precursor
		if self.parse_result: yield parse_result

	def char(self):
		self.parse_result = self.sp.next_char()
		return StreamParseResult(self.sp, self)

	def int(self):
		self.parse_result = self.sp.next_int()
		return StreamParseResult(self.sp, self)

	def token(self):
		self.parse_result = self.sp.next_token()
		return StreamParseResult(self.sp, self)
	
def ignore_whitespace(method):
	""" Add an ignore_whitespace = True to some method of StreamParser.
		If this is True, consume characters while they are whitespace
		(space, tab, CR, newline). """
	@functools.wraps(method)
	def with_whitespace(self, *args, ignore_whitespace=True, **kwargs):
		if ignore_whitespace:
			while self.stream and self.peek_char() in string.whitespace:
				self.next_char()
		return method(self, *args, **kwargs)
	return with_whitespace


class StreamParser:
	""" A class to help parse streams of input and output. """
	NUMERIC = "0123456789"
	def __init__(self, string):
		self.stream = collections.deque(string)

	def __bool__(self):
		return bool(self.stream)

	def peek_char(self):
		""" 
		Return the next character in the stream, or raise a StreamParseError
		if there are none.
		"""
		if self.stream:
			return self.stream[0]
		else:
			raise StreamParseError()

	def is_next_char_in(self, charset):
		"""
		Returns True if and only if the next character of the stream is in charset.
		"""
		return self.stream and self.peek_char() in charset

	def is_next_char_not_in(self, charset):
		"""
		Returns True if and only if the next character of the stream is not in charset.
		"""
		return self.stream and self.peek_char() not in charset

	
	def next_char(self):
		"""
		Return the next character in the stream, and remove it.
		"""
		char_read = self.peek_char()
		self.stream.popleft()
		return char_read

	@ignore_whitespace
	def next_int(self):
		"""
		Parse and return an integer from the stream.
		"""
		isNegative = self.peek_char() == "-"
		digits = ""
		while self.is_next_char_in(string.digits):
			digits += self.next_char()

		if not digits:
			return StreamParseError()

		answer = int(digits)
		if isNegative:
			answer *= -1
		return answer
	
	@ignore_whitespace
	def next_token(self, delims = ' \t\n', strip_delim = True):
		"""
		Parse and return a token delimited by any character in delims (by default, whitespace).
		This method consumes the delimiter. If strip_delim is True, the delimiter will be removed
		from the return value.
		"""
		token = ""
		while self.is_next_char_not_in(delims):
			token += self.next_char()
		if self.is_next_char_in(delims):	# consume the delimiter
			self.next_char()
		
		if strip_delim:
			token.strip(delims)
		return token

	@ignore_whitespace
	def next_string(self, charset):
		"""
		Parse and return a string whose characters are in charset.
		"""
		answer = ""
		while self.is_next_char_in(charset):
			answer += self.next_char()
		return answer

	def read(self):
		return StreamParserChain(self)

def read_input_as_streams(checker):
	"""
	Takes in a checker function that works with StreamParsers, and 
	makes them work with strings, as Program.stress_test expects.
	"""
	@functools.wraps(checker)
	def streamified(inp, correct, out):
		inp = StreamParser(inp)
		correct = StreamParser(correct)
		out = StreamParser(out)
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
