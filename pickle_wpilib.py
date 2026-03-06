import logging
import pickle
import sys
import time

from battery_analysis import yield_samples_from_datalog


def main(argv):
    samples = []
    t0 = time.time()
    for battery_data_sample in yield_samples_from_datalog('data/FRC_20260305_005905.wpilog'):
        samples.append(battery_data_sample)
    print('read wpilib', time.time() - t0)
    t0 = time.time()
    with open('test.pickle', 'wb') as f:
        pickle.dump(samples, f)
    print('write', time.time() - t0)

    del samples
    t0 = time.time()
    with open('test.pickle', 'rb') as f:
        samples = pickle.load(f)
    print('read pickle', time.time() - t0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    main(sys.argv[1:])

