import logging
import sys

from battery_analysis import yield_from_datalog

def main():
    previous_w = None

    values = {}

    j = 0

    for t in yield_from_datalog('FRC_20260222_221544.wpilog'):
        timestamp, name, v, _, _ = t
        if name == '/Robot/hb':
            # all done sampling!
            w = values.get('/Robot/pdb/w')
            if previous_w is not None:
                t = (w[0] - previous_w[0])  # time interval between samples
                average_wattage_over_interval = (w[1] + previous_w[1]) / 2
                j = j + (t * average_wattage_over_interval)
            previous_w = w
            pdh_energy = values.get('/Robot/pdb/j')
            print(','.join(str(v) for v in (timestamp, pdh_energy[1], j)))
        else:
            values[name] = (timestamp, v)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    main()

