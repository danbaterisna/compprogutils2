import sys
from .compile import cpp_compile
from .program import Program

from .presentation import cpu_print
from termcolor import colored

def main():
	if sys.argv[1] == "comp":
		cpp_compile(sys.argv[2])
	elif sys.argv[1] == "compf":
		cpp_compile(sys.argv[2], preset = "fast")
	elif sys.argv[1] == "compt":
		if cpp_compile(sys.argv[2]):
			Program(f"./{sys.argv[2]}.exe").run()
	elif sys.argv[1] == "compft" or sys.argv[1] == "comptf":
		if cpp_compile(sys.argv[2], preset = "fast"):
			Program(f"./{sys.argv[2]}.exe").run()
	else:
		cpu_print(colored(f"{sys.argv[1]} is an unknown command", "red"), file=sys.stderr)


if __name__ == "__main__":
	main()
	
