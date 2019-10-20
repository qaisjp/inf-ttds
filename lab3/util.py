import sys

def safe_int(x):
    try:
        return int(x)
    except ValueError:
        return x

def get_file_lines(filename):
    with open(filename) as f:
        return [line.rstrip() for line in f]

# From https://stackoverflow.com/a/14981125
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
