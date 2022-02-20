# compprogutils2

A set of scripts to help with my competitive programming workflow.

[The one I made a few years prior](https://github.com/danbaterisna/compprogutils) was overengineered, and too clunky to be of practical use. 
This is also probably overengineered, but I hope the interface is more practical.

## Installation

Clone this repository, then, in the same directory as `setup.py`, run

```bash
pip install --prefix=$(python3 -m site --user-base) -e .
```

## Usage

### Compilation

```bash
cpu comp A # Compiles A.cpp, generating an A.exe executable
cpu compf A # Compiles A.cpp, optimizing for speed
cpu compt A # Equivalent to cpu comp A && ./A.exe
cpu compft A # Equivalent to cpu compf A && ./A.exe
```

The compilation commands are as follows:
```bash
# normal
g++ -std=c++17 -Wall -g {filename} -o {program_name}.exe -fsanitize=address,undefined -D__GLIBCXX_DEBUG
# fast
g++ -std=c++17 -O2 -Wall -g {filename} -o {program_name}.exe
```

If two `comp/compt` commands are issued on the same file, and the file has not changed between the commands, cpu will not recompile the program
on the second invocation. `compf/compft` shows similar behavior. (However, `cpu comp A && cpu compf A`) will compile the program twice.

### Profiling 

```python
from random import randint
from cpu import *

p1 = Program("./A.exe") # Command used to execute the program
p2 = Program("./A_brute.exe")

@generator
def inpgen(print):
  n = randint(1, 50)
  print(n)
  print(*[randint(1, 50) for i in range(n)])
  
p1.profile(inpgen, run_count=10)

p1.stress_test(p2, inpgen, run_count=10) # p1 generates correct output
```

The `profile` and `stress_test` methods accept other several optional parameters:
- `write_input_file`: if `True`, writes the input used in the most recent run to a suitably named file.
  By default, this is `False` in `profile`, while this is `True` in `stress_test`.
- (Only for `stress_test`) `checker`: a function that takes in three strings: the input, the correct output, and the stressed program's output.
  This function should return a number that is 1 if the output is considered correct, and 0 otherwise. By default, this is `token_checker`, 
  which checks that the two outputs match aside from whitespace. Custom checkers may use the `read_input_as_streams` decorator,
  which converts the strings into `StringStream`s.

### Interaction

The following is a sample interactor for testing a submission to [CF 525 Div 2 D](https://codeforces.com/problemset/problem/1088/D):

```python
from cpu import *
from random import randint

a, b = [randint(0, 2**10 - 1) for c in range(2)]
qcount = 0
with RunningProgram(["./CF1088D.exe"]) as r:
  while True:
    [t, c, d] = r.out.read().token().int().int()
    if t == '!':
      print("output", c, d, "answer", a, b)
      break
    else:
      x, y = a^c, b^d
      if x < y:
        r.input(-1)
      elif x == y:
        r.input(0)
      else`
        r.input(1)
      qcount += 1
print("Program finished in", qcount, "queries")
```
Note that `RunningProgram` returns an object with `input` and `out` methods. `input` can be used to supply input to the program. 
  It can take variable positional arguments like `print`, as well as `sep` and `end` keyword arguments.
  `out` is a `ProgramStream` attached to the program's output.
  
### Parsers

cpu has two classes for parsing input/output streams:
- `StringStream`, for reading output from a string, obtained via a batch run of a `Program`.
- `ProgramStream`, for taking output from a `RunningProgram`.

The two share the same API; refer to `parser.py`. However, `ProgramStream` may block to wait for input.

The `read()` method returns an object that supports chaining, as illustrated here.

## TODO

- `comp[f][t]`, `[Running]Program` support for other languages
- `printf-to-cout` and vice versa converters
- `cpu library` to output template code
- Testing
