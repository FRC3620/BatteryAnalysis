import itertools
import logging
import statistics
import time
import sys

from typing import List

from battery_analysis import yield_samples_from_datalog, yield_samples_from_file, BatteryDataSample

class BatteryDataSampleCollection:
    def __init__(self):
        self.samples : List[BatteryDataSample] = []
        self.t0 = None
        self.t_last = None
        self.extras = {}

    def add(self, battery_data_sample : BatteryDataSample = None):
        self.samples.append(battery_data_sample)
        ts = battery_data_sample.timestamp
        self.t0 = ts if self.t0 is None else min(self.t0, ts)
        self.t_last = ts if self.t_last is None else max(self.t_last, ts)


def calculate_no_load(collection : BatteryDataSampleCollection):
    if collection.t_last - collection.t0 < 2.5:
        return None
    # samples = itertools.filterfalse(lambda s: abs(s.timestamp - collection.t_last) > 0.5, collection.samples)
    # v = statistics.mean(sample.item('/Robot/v').value for sample in samples)
    v = collection.samples[-1].item('/Robot/v').value
    return v


def calculate_rint(collection : BatteryDataSampleCollection, v_noload : float):
    for sample in collection.samples:
        v_drop = v_noload - sample.item('/Robot/v').value
        current = sample.total_heater_current()
        if current > 0:
            print("rint", v_drop/current, v_drop, current)


def main(argv):
    collections = []

    collection = BatteryDataSampleCollection()
    collection.extras['is_on'] = False
    collections.append(collection)

    t0 = time.time()
    for battery_data_sample in yield_samples_from_file('test.pickle'):  # 'data/FRC_20260305_005905.wpilog'):
        total_setpoint = 0
        for battery_data_item in battery_data_sample.items_matching(r'/Robot/H\d+/setpoint'):
            # print(battery_data_item)
            total_setpoint += battery_data_item.value

        is_on = total_setpoint > 0
        if is_on != collection.extras['is_on']:
            collection = BatteryDataSampleCollection()
            collections.append(collection)
            collection.extras['is_on'] = is_on

        collection.add(battery_data_sample)

    for collection in collections:
        is_on = collection.extras['is_on']
        if not is_on:
            no_load_v = calculate_no_load(collection)
            print("no_load_v", no_load_v)
        else:
            if no_load_v is not None:
                calculate_rint(collection, no_load_v)

    print('time', time.time() - t0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    main(sys.argv[1:])

