import subprocess, time, sys, pathlib

from .presentation import cpu_print, cpu_progress
from .checker import token_checker
from termcolor import colored
from tqdm import tqdm

class Program:
	""" Wrapper class for dealing with batch programs. """

	def __init__(self, path_to_exec):
		self.path_to_exec = path_to_exec

	def program_name(self):
		return str(pathlib.Path(self.path_to_exec).with_suffix(''))

	def run(self):
		""" Runs the program, piping output to standard output. """
		try:
			subprocess.run([self.path_to_exec])
		except KeyboardInterrupt:
			cpu_print("Interrupted", file=sys.stderr)

	def batch_run(self, program_input):
		""" Run the program with a given string (or bytes-like object) as input. Return the output. """
		try:
			program_status = subprocess.run([self.path_to_exec], input=program_input, capture_output=True,
				check=True, text=True)
			return program_status.stdout
		# The function will return None if either of these are triggered
		except KeyboardInterrupt:
			cpu_print("Interrupted", file=sys.stderr)
		except subprocess.CalledProcessError:
			cpu_print(f"Program {self.path_to_exec} exited with non-zero status", file=sys.stderr)
		
			
	def _generate_input_for_program(self, input_generator, write_input_file):
		"""
		Use the input_generator to generate an input file to associate with this program.
		input_generator: A function that returns a bytearray-like object to pass into the program.
		write_input_file: If set to True, will write out the result of input_generator
				to a file named `input_{path_to_exec}.txt`
		"""
		program_input = input_generator()
		if write_input_file:
			input_filename = f"input_{self.program_name()}.txt"
			with open(input_filename, "wb") as input_file:
				input_file.write(program_input.encode("utf-8"))
		return program_input

	def _perform_profiling_run(self, program_input):
		""" Performs one profiling run with the given input.
			Returns:
				-1 if program did not finish without errors,
				A float, denoting the time taken to finish.
		"""
		try:
			start_time = time.time()
			program_status = subprocess.run([self.path_to_exec], input=program_input,
				stdout=subprocess.DEVNULL, check=True, text=True)
			return time.time() - start_time
		except subprocess.CalledProcessError:
			cpu_print("Program exited with non-zero status, aborting profiling", file=sys.stderr)
			return -1
		except KeyboardInterrupt:
			cpu_print("Profiling interrupted", file=sys.stderr)
			return -1

	def profile(self, input_generator, run_count=1, write_input_file=False):
		""" Profiles the performance of the program.
			input_generator: A function that returns a bytearray-like object
				to pass into the program.
			run_count: The number of runs to use to measure performance.
			write_input_file: If set to True, will write out the result of input_generator
				to a file named `input_{path_to_exec}.txt`. """
		if run_count <= 0:
			return
		cpu_print(colored(f"Performing {run_count} profiling runs on {self.path_to_exec}", "blue"),
			file=sys.stderr)
		runtimes = []
		for run_index in cpu_progress(range(run_count), "Profiling runs"):
			# print("Doing run ", run_index, file=sys.stderr)
			program_input = self._generate_input_for_program(input_generator, write_input_file)
			time_taken = self._perform_profiling_run(program_input)
			if time_taken == -1:
				return
			runtimes.append(time_taken)
			# print(f"Run finished in {time_taken:.2}", file=sys.stderr)
		cpu_print(f"max {max(runtimes):.2} min {min(runtimes):.2} avg {sum(runtimes)/len(runtimes):.2}",
			file=sys.stderr)
		
	def stress_test(self, program, input_generator, checker=token_checker, run_count=100, write_input_file=True):
		""" Stress tests `program`, using this Program as a correct input generator.
			program: The program to check correctness for.
			input_generator: A function that returns a bytearray-like object
				to pass into the program.
			checker: A function that takes in the generated input, 
				this Program's output, and program's output, and returns a score. 1 is an AC,
				and anything below is WA.
		"""			
		if run_count <= 0:
			return 
		cpu_print(colored(f"Performing {run_count}-run stress test on {program.path_to_exec} using {self.path_to_exec}", "blue"),
			file=sys.stderr)
		for run_index in cpu_progress(range(run_count), "Stress tests"):
			program_input = self._generate_input_for_program(input_generator, write_input_file)
			correct_output = self.batch_run(program_input)
			stressee_output = program.batch_run(program_input)
			if correct_output is None or stressee_output is None:
				cpu_print(colored("RTE detected, aborting stress test", "yellow"), file=sys.stderr)
				return 
			checker_result = checker(program_input, correct_output, stressee_output)
			if checker_result < 1:
				cpu_print(colored(f"WA on run {run_index}", "red"), file=sys.stderr)
				if write_input_file:
					cpu_print(colored(f"Breaking TC generated in input_{self.program_name()}.txt", "red"), file=sys.stderr)
				break
		else:
			cpu_print(colored("Stress test found no errors", "green"), file=sys.stderr)

