from setuptools import setup
	
setup( 
	name="cpu",
	version="0.0.1",
	packages = ["cpu"],
	install_requires = [
		"colorama",
		"termcolor",
		"tqdm"
	],
	entry_points = """
		[console_scripts]
		cpu=cpu:__main__.main
	""",
)
