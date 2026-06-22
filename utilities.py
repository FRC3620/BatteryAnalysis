import logging
import pickle
import re
import sys

from typing import Self, Dict, Iterator

from frc3620_wpilog import DataLogDatum, datalog_datum_iterator


class MeanThing:
    def __init__(self, window_size=None):
        self.v = []
        self.window_size = window_size

    def add(self, v):
        self.v.append(v)
        if self.window_size is not None and len(self.v) > self.window_size:
            del self.v[0]

    def mean(self):
        return sum(self.v)/len(self.v)


class ConsecutiveLT:
    def __init__(self, n : int = 3, threshold : float = None):
        self.n = n
        self.i = 0
        self.threshold = threshold

    def in_a_row(self, v):
        if v < self.threshold:
            self.i = self.i + 1
        else:
            self.i = 0
        return self.i >= self.n


class BatteryDataSample:
    def __init__(self, template: Self = None):
        self.battery_data_items : Dict[str, DataLogDatum] = {}
        self.timestamp = None
        if template is not None:
            self.battery_data_items = template.battery_data_items.copy()
            self.timestamp = template.timestamp

    def add(self, battery_data_item : DataLogDatum):
        self.battery_data_items[battery_data_item.name] = battery_data_item

    def items(self):
        for battery_data_item in self.battery_data_items:
            yield battery_data_item

    def items_matching(self, pattern):
        regexp = re.compile(pattern)
        for name, battery_data_item in self.battery_data_items.items():
            if regexp.fullmatch(name):
                yield battery_data_item

    def item(self, name : str = None) -> DataLogDatum:
        return self.battery_data_items.get(name)

    def total_heater_current(self):
        rv = 0
        for battery_data_item in self.items_matching(r'/Robot/H\d+/input/a'):
            rv += battery_data_item.value
        return rv


def yield_samples_from_datalog(filename : str = None) -> Iterator[BatteryDataSample]:
    """

    :param filename: name of the file to read from
    :return:
    """
    rv = BatteryDataSample()
    for t in datalog_datum_iterator(filename):
        battery_data_item = t[0]
        rv.add(battery_data_item)
        if battery_data_item.name == '/Robot/hb':
            rv.timestamp = battery_data_item.timestamp
            yield BatteryDataSample(rv)

def yield_samples_from_pickle(filename : str = None) -> Iterator[BatteryDataSample]:
    with open(filename, 'rb') as fp:
        samples = pickle.load(fp)
        for sample in samples:
            yield(sample)

def yield_samples_from_file(filename : str = None) -> Iterator[BatteryDataSample]:
    if filename.endswith('.wpilog'):
        for s in yield_samples_from_datalog(filename):
            yield s
    elif filename.endswith('.pickle'):
        for s in yield_samples_from_pickle(filename):
            yield s
    else:
        raise Exception(f"don't know how to read '{filename}'")


def main(argv):
    threshold = 10.90
    sm = MeanThing(window_size=100)
    in_a_row = ConsecutiveLT(n=9, threshold=threshold)
    for battery_data_sample in yield_samples_from_datalog('data/FRC_20260305_005905.wpilog'):
        robot_v = battery_data_sample.item('/Robot/v')
        vv = robot_v.value
        slm = sm.add(vv)
        #print(','.join(str(v) for v in (battery_data_sample.timestamp, vv, slm, slm < threshold, in_a_row.in_a_row(vv))))

        print(battery_data_sample.item('/Robot/pdb/v'))
        for battery_data_item in battery_data_sample.items_matching(r'/Robot/H\d+/input/v'):
            #print(battery_data_item)
            pass

        for battery_data_item in battery_data_sample.items_matching(r'/Robot/H\d+/input/a'):
            #print(battery_data_item)
            pass
        #print (battery_data_sample.total_heater_current())
        #print(battery_data_sample.item('/Robot/pdb/a'))

        for battery_data_item in battery_data_sample.items_matching(r'/Robot/H\d+/setpoint'):
            print(battery_data_sample.timestamp, battery_data_item)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    main(sys.argv[1:])
