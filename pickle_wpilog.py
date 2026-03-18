import argparse
import glob
import logging
import pickle
import sys
import time

from utilities import yield_samples_from_datalog


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--test', action='store_true')
    parser.add_argument('inglob')
    args = parser.parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    for filename in glob.glob(args.inglob):
        samples = []
        t0 = time.time()
        for battery_data_sample in yield_samples_from_datalog(filename):
            samples.append(battery_data_sample)
        logging.info('%s read: %s seconds, %s samples', filename, time.time() - t0, len(samples))

        outfile = filename + '.pickle'

        t0 = time.time()
        with open(outfile, 'wb') as f:
            pickle.dump(samples, f)
        logging.info('%s written: %s seconds', outfile, time.time() - t0)

        if args.test:
            del samples
            t0 = time.time()
            with open(outfile, 'rb') as f:
                samples = pickle.load(f)
            logging.info('%s read: %s seconds, %s samples', outfile, time.time() - t0, len(samples))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    main(sys.argv[1:])
