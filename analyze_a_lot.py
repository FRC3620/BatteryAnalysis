import argparse
import glob
import logging
import sys

import analyze

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('inglob', nargs='+')
    args = parser.parse_args(argv)

    for inglob1 in args.inglob:
        for f in glob.glob(inglob1):
            sargs = []
            if args.verbose:
                sargs.append('-v')
            sargs.append(f)
            try:
                analyze.main(sargs)
            except Exception as e:
                logging.error('trouble processing %s', f, exc_info=e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    main(sys.argv[1:])