import argparse
import os.path
import sys

from results import read_results, read_relevant

class TTDS():
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='TTDS Coursework 2',
            usage='''app.py <command> [<args>]

The most commonly used commands are:
    parse   Parse dem files
''')

        parser.add_argument('command', help='Subcommand to run')

        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)

        getattr(self, args.command)(sys.argv[2:])

    def parse(self, args):
        parser = argparse.ArgumentParser(
            description='parse dem files')

        # parser.add_argument('tweetfile', help="prefix file to use")
        # parser.add_argument('--refresh-dic', action='store_true')

        args = parser.parse_args(args)

        with open("S1.results", "r") as f:
            retrieved = read_results(f)
        with open("qrels.txt") as f:
            relevant = read_relevant(f)




if __name__ == "__main__":
    TTDS()
