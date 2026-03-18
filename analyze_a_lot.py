import argparse
import glob
import logging
import sys

import analyze

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('inglob')
    args = parser.parse_args(argv)

    for f in glob.glob(args.inglob):
        sargs = []
        if args.verbose:
            sargs.append('-v')
        sargs.append(f)
        analyze.main(sargs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    main(sys.argv[1:])