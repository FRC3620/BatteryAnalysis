import argparse
import datetime
import logging
import os.path
import time
import sys

from typing import List

from wpilogwriter import SmartWPILogWriter, WPILogWriter

from utilities import yield_samples_from_file, BatteryDataSample

class G:
    def __init__(self):
        self.j_start = None
        self.soc_start = None
        self.j_end = None
        self.soc_end = None
        self.v_noload = None


class BatteryDataSampleCollection:
    def __init__(self):
        self.samples: List[BatteryDataSample] = []
        self.t0 = None
        self.t_last = None
        self.extras = {}

    def add(self, sample: BatteryDataSample = None):
        self.samples.append(sample)
        ts = sample.timestamp
        self.t0 = ts if self.t0 is None else min(self.t0, ts)
        self.t_last = ts if self.t_last is None else max(self.t_last, ts)


def log_input_data(sample: BatteryDataSample, w: WPILogWriter):
    total_setpoint = 0
    ts = sample.item('/Robot/hb').timestamp
    for battery_data_item in sample.items_matching(r'/Robot/H\d+/setpoint'):
        w.log(battery_data_item.timestamp, battery_data_item.name, battery_data_item.value)
        total_setpoint += battery_data_item.value
    w.log(ts, '/analysis/total_setpoint', total_setpoint)
    for battery_data_item in sample.items_matching(r'/Robot/H\d+/input/a'):
        w.log(battery_data_item.timestamp, battery_data_item.name, battery_data_item.value)
    for regexp in (r'/Metadata/.*', ):
        for item in sample.items_matching(regexp):
            w.log(item.timestamp, item.name, item.value)
    for name in ('/Robot/mode', '/Robot/v', '/Robot/H/a', '/Robot/H/setpoint', '/Robot/batteryId', '/Robot/pdb/j',
                 '/Robot/pdb/a', '/Robot/pdb/v', 'systemTime'):
        v = sample.item(name)
        if v is not None:
            w.log(v.timestamp, v.name, v.value)


def calculate_soc(v):
    return (v - 11.75) / 1.25


def process_no_load(collection: BatteryDataSampleCollection, w: WPILogWriter, g: G = None):
    if collection.extras['is_on']:
        raise ValueError()
    if len(collection.samples) == 0:
        logging.warn('got collection with no samples')
        return
    w.log(collection.t0, 'is_on', collection.extras['is_on'])
    v_noload = 0
    j_at_max_v_noload = None
    for sample in collection.samples:
        voltage = sample.item('/Robot/v').value
        j = sample.item('/Robot/pdb/j').value
        if voltage > v_noload:
            v_noload = voltage
            j_at_max_v_noload = j

        v_noload = max(v_noload, voltage)
        ts = sample.item('/Robot/hb').timestamp

        log_input_data(sample, w)
        w.log(ts, '/analysis/v_noload', v_noload)
        w.log(ts, '/analysis/v_drop', 0.0)

        soc = calculate_soc(voltage)

        w.log(ts, '/analysis/soc', soc)

        if g.soc_start is not None:
            g.soc_end = soc
            g.j_end = j
            w.log_float(ts, '/analysis/j_start', g.j_start)
            w.log_float(ts, '/analysis/j_end', g.j_end)
            w.log_float(ts, '/analysis/soc_start', g.soc_start)
            w.log_float(ts, '/analysis/soc_end', g.soc_end)

            soc_delta = g.soc_start - g.soc_end
            w.log_float(ts, '/analysis/soc_delta', soc_delta)
            if soc_delta > 0:
                j_delta = g.j_start - g.j_end
                capacity_estimate = -j_delta / soc_delta
                w.log_float(ts, '/analysis/j_delta', -j_delta)
                w.log_float(ts, '/analysis/capacity_estimate', capacity_estimate)

    soc = calculate_soc(v_noload)
    if g.soc_start is None and soc < 1.00:
        g.soc_start = soc
        g.j_start = j_at_max_v_noload

    g.v_noload = None if v_noload == 0 else v_noload


def process_load(collection: BatteryDataSampleCollection, w: WPILogWriter, g: G = None):
    if not collection.extras['is_on']:
        raise ValueError()
    if len(collection.samples) == 0:
        logging.warn('got collection with no samples')
        return
    w.log(collection.t0, 'is_on', collection.extras['is_on'])
    for sample in collection.samples:
        log_input_data(sample, w)
        if g.v_noload is not None:
            v_drop = g.v_noload - sample.item('/Robot/v').value
            current = sample.total_heater_current()
            if current > 0:
                rint = v_drop/current
                ts = sample.item('/Robot/hb').timestamp
                w.log(ts, '/analysis/rint', rint)
                w.log(ts, '/analysis/v_drop', v_drop)
                w.log(ts, '/analysis/current', current)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--output', '-o')
    parser.add_argument('infile')
    args = parser.parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logging.info("reading %s", args.infile)

    collections = []

    collection = BatteryDataSampleCollection()
    collection.extras['is_on'] = False
    collections.append(collection)

    t0 = time.time()

    batteryId_item = None
    run_dt = None

    for sample in yield_samples_from_file(args.infile):
        setpoint = sample.item('/Robot/H/setpoint').value
        robot_mode = sample.item('/Robot/mode').value

        is_on = setpoint > 0 and robot_mode != 'DISABLED'
        if is_on != collection.extras['is_on']:
            collection = BatteryDataSampleCollection()
            collections.append(collection)
            collection.extras['is_on'] = is_on

        collection.add(sample)

        systemTime = sample.item('systemTime')
        if systemTime is not None and run_dt is None:
            start_time = (systemTime.value / 1000000) - systemTime.timestamp
            run_dt = datetime.datetime.fromtimestamp(start_time)
            logging.info("test started at %s", run_dt)

        batteryId_item = sample.item('/Robot/batteryId')

    if batteryId_item is None or batteryId_item.value == -1:
        raise ValueError("no /Robot/batteryId")

    if run_dt is None:
        raise ValueError("no systemTime")

    if args.output:
        outfile = args.output
    else:
        outfile = f'{os.path.dirname(args.infile)}/#{batteryId_item.value}_{run_dt.strftime("%Y%m%d-%H%M%S")}.wpilog'
    logging.info("writing %s", outfile)
    w = SmartWPILogWriter(outfile)

    g = G()
    for collection in collections:
        is_on = collection.extras['is_on']
        if not is_on:
            process_no_load(collection, w=w, g=g)
        else:
            process_load(collection, w=w, g=g)

    logging.info("processing took %s seconds", time.time() - t0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    main(sys.argv[1:])

