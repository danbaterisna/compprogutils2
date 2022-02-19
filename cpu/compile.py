import hashlib, subprocess, pathlib, sys, functools

from .presentation import cpu_print
from termcolor import colored

PREVIOUS_HASH_ENV_VAR_NAME = "COMP_PROG_UTIL_RECENT_PROGRAM"
DATA_FILE_PATH = pathlib.Path(pathlib.Path.home(), ".cpu_data")

def ensure_datafile_exists(f):
	@functools.wraps(f)
	def with_config(*args, **kwargs):
		if not DATA_FILE_PATH.exists():
			DATA_FILE_PATH.touch()
		return f(*args, **kwargs)
	return with_config

@ensure_datafile_exists
def get_previous_hash():
	with open(str(DATA_FILE_PATH), "rb") as datafile:
		return datafile.read()

@ensure_datafile_exists
def set_current_hash(current_hash):
	with open(str(DATA_FILE_PATH), "wb") as datafile:
		datafile.write(current_hash)


def hash_program(filename, preset):
	with open(filename, "rb") as file_to_hash:
		file_data = preset.encode("utf-8") + file_to_hash.read()		
		file_hash = hashlib.sha256(file_data).hexdigest()
	return file_hash.encode("utf-8")
		

def should_recompile(filename, preset):
	previous_compile_hash = get_previous_hash()
	current_hash = hash_program(filename, preset)
	return previous_compile_hash != current_hash


def cpp_compile(program_name, preset = "normal"):
	
	filename = f"{program_name}.cpp"

	PRESETS = {
		"normal": "g++ -std=c++17 -Wall -g {filename} -o {program_name}.exe -fsanitize=address,undefined -D__GLIBCXX_DEBUG",
		"fast": "g++ -std=c++17 -O2 -Wall -g {filename} -o {program_name}.exe",
	}

	if not pathlib.Path(filename).exists():
		cpu_print(colored(f"{filename} does not exist, stopping", "red"), file=sys.stderr)
		return False

	if should_recompile(filename, preset):
		cpu_print(colored(f"Recompiling {filename}", "blue"), file=sys.stderr)
		COMMAND = PRESETS[preset].format(filename=filename, program_name=program_name).split()
		try:
			subprocess.run(COMMAND, check=True)
		except subprocess.CalledProcessError:
			return False
		cpu_print(colored("Recompilation complete", "green"), file=sys.stderr)
		set_current_hash(hash_program(filename, preset))

	return True
