def safe_int(x):
    try:
        return int(x)
    except ValueError:
        return x

def get_file_lines(filename):
    with open(filename) as f:
        return [line.rstrip() for line in f]
