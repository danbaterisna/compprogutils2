import abc
import collections, functools, string

class StreamParseError(Exception):
	""" Raised when one of the default StreamParsers raises an error. """
	pass

class StreamParserChain:
	""" A helper class that facilitates the chaining of StreamParser methods. """
	def __init__(self, sp, precursor = None):
		self.sp = sp
		self.precursor = precursor
		self.parse_result = None
	
	def __iter__(self):
		if self.precursor: yield from self.precursor
		if self.parse_result is not None: yield self.parse_result

	def char(self):
		self.parse_result = self.sp.next_char()
		return StreamParserChain(self.sp, self)

	def int(self):
		self.parse_result = self.sp.next_int()
		return StreamParserChain(self.sp, self)

	def token(self):
		self.parse_result = self.sp.next_token()
		return StreamParserChain(self.sp, self)
	
def ignore_whitespace(method):
	""" Add an ignore_whitespace = True to some method of StreamParser.
		If this is True, consume characters while they are whitespace
		(space, tab, CR, newline). """
	@functools.wraps(method)
	def with_whitespace(self, *args, ignore_whitespace=True, **kwargs):
		if ignore_whitespace:
			while self and str(self.peek_char()) in string.whitespace:
				self.next_char()
		return method(self, *args, **kwargs)
	return with_whitespace


class StreamParser(abc.ABC):
	""" A class to help parse streams of input and output. """
	NUMERIC = "0123456789"
	def __init__(self):
		...	

	@abc.abstractmethod
	def __bool__(self):
		"""
		Return True iff the stream might contain some characters.
		"""
		raise NotImplementedError("Child of StreamParser must override __bool__")

	@abc.abstractmethod
	def peek_char(self):
		""" 
		Return the next character in the stream, or raise a StreamParseError
		if there are none.
		"""
		raise NotImplementedError("Child of StreamParser must override peek_char")

	
	@abc.abstractmethod
	def pop_char(self):
		"""
		Remove the next character in the stream.
		"""
		raise NotImplementedError("Child of StreamParser must override pop_char")

	def is_next_char_in(self, charset):
		"""
		Returns True if and only if the next character of the stream is in charset.
		"""
		return self and str(self.peek_char()) in charset

	def is_next_char_not_in(self, charset):
		"""
		Returns True if and only if the next character of the stream is not in charset.
		"""
		return self and str(self.peek_char()) not in charset
	
	def next_char(self):
		"""
		Return the next character in the stream, and remove it.
		"""
		next_char = self.peek_char()
		self.pop_char()
		return next_char

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

class StringStream(StreamParser):
	def __init__(self, string):
		super().__init__()
		self.stream = collections.deque(string)

	def __bool__(self):
		return bool(self.stream)

	def peek_char(self):
		if self.stream:
			return self.stream[0]
		else:
			raise StreamParseError()

	def pop_char(self):
		self.stream.popleft()
	

class ProgramStream(StreamParser):
	def __init__(self, prog):
		super().__init__()
		self.input_queue = prog.stdout_queue
		self.prog = prog
		self.head_char = None
	
	def __bool__(self):
		return not self.prog.stdout_queue_finished

	def peek_char(self):
		if self:
			if not self.head_char:
				self.head_char = self.input_queue.get()
			return self.head_char.decode("UTF-8")
		else:
			raise StreamParseError()

	def pop_char(self):
		self.head_char = None
