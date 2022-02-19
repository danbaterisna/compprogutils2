from colorama import init, Cursor
from termcolor import colored
from tqdm import tqdm

init()

PREFIX = colored("[cpu]", "yellow")

def cpu_print(*args, **kwargs):
	print(PREFIX, *args, **kwargs)

def cpu_progress(iterable, desc):
	return tqdm(iterable, desc=PREFIX + " " + desc, colour="yellow")

