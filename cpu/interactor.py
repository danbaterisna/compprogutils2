import threading, queue, subprocess, functools

from .parser import ProgramStream

class RunningProgramInterface:
	"""
	Class for sending input to and reading output from interactive programs.
	The __enter__ method of RunningProgram will return a RunningProgramInterface.

	This has an `in` method, which prints to the program, and an `out` member,
	which is a ProgramStream associated with the program's output.
	"""
	def __init__(self, prog):
		self.prog = prog
		self.out = ProgramStream(prog)

	def input(self, *args, sep=' ', end="\n"):
		""" Feeds in the string to the program, as if via print."""
		input_line = sep.join(str(arg) for arg in args) + end
		self.prog.proc.stdin.write(input_line.encode("UTF-8"))
		self.prog.proc.stdin.flush()


class RunningProgram:
	""" Wrapper class for dealing with interactive programs. This runs the programs
	on a separate thread. 

	This must be used within a context manager, to automate the cleanup
	of the threads it internally uses.
	"""
	def __init__(self, program_args):
		self.proc = subprocess.Popen(program_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		self.stdout_queue = queue.Queue()
		self.stdout_queue_finished = False
		self.stdout_read_thread = threading.Thread(target = self._stdout_read_thread)
		self.stderr_read_thread = threading.Thread(target = self._stream_output_thread,
			args = (self.proc.stderr,))

	def _stdout_read_thread(self):
		while True:
			data = self.proc.stdout.read(1)
			if not data:
				return
			self.stdout_queue.put(data)
		self.stdout_queue_finished = True

	def _stream_output_thread(self, stream):
		new_line = True
		while True:
			data = stream.read(1024)
			if not data:
				return
			data = data.decode("UTF-8")
			if new_line:
				data = colored(str(program_args), "blue") + data
				new_line = False
			sys.stderr_write(data)
			if data.endswith("\n"):
				new_line = True
			sys.stderr.flush()
				
	def __enter__(self):
		self.stdout_read_thread.start()
		self.stderr_read_thread.start()

		return RunningProgramInterface(self)

	def __exit__(self, type, value, traceback):
		
		if self.proc.poll() is None:
			self.proc.terminate()

		self.stdout_read_thread.join()
		self.stderr_read_thread.join()
