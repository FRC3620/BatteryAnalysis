import argparse
import datetime
import logging
import os.path
import time
import sys

from typing import List

from wpilogwriter import SmartWPILogWriter, WPILogWriter

from utilities import yield_samples_from_file, BatteryDataSample, MeanThing

class G:
    def __init__(self):
        self.j_start = None
        self.soc_start = None
        self.j_end = None
        self.soc_end = None
        self.v_noload = None
        self.v_load = None
        self.i_load = None
        self.t_offset = None
        self.fake_t = 0

    def t(self, ts):
        new_ts = ts + self.t_offset
        if new_ts < 0:
            new_ts = self.fake_t
            self.fake_t += 0.000001
        return new_ts


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


def log_input_data(sample: BatteryDataSample, w: WPILogWriter, g : G = None):
    total_setpoint = 0
    ts = sample.item('/Robot/hb').timestamp
    for battery_data_item in sample.items_matching(r'/Robot/H\d+/setpoint'):
        w.log(g.t(battery_data_item.timestamp), battery_data_item.name, battery_data_item.value)
        total_setpoint += battery_data_item.value
    w.log(ts + g.t_offset, '/analysis/total_setpoint', total_setpoint)
    for battery_data_item in sample.items_matching(r'/Robot/H\d+/input/a'):
        w.log(g.t(battery_data_item.timestamp), battery_data_item.name, battery_data_item.value)
    for regexp in (r'/Metadata/.*', ):
        for item in sample.items_matching(regexp):
            w.log(g.t(item.timestamp), item.name, item.value)
    for name in ('/Robot/mode', '/Robot/v', '/Robot/H/a', '/Robot/H/setpoint', '/Robot/batteryId', '/Robot/pdb/j',
                 '/Robot/pdb/a', '/Robot/pdb/v', 'systemTime'):
        v = sample.item(name)
        if v is not None:
            w.log(g.t(v.timestamp), v.name, v.value)


def calculate_soc(v):
    return (v - 11.75) / 1.25


def process_no_load(collection: BatteryDataSampleCollection, w: WPILogWriter, g: G = None):
    if collection.extras['is_on']:
        raise ValueError()
    if len(collection.samples) == 0:
        logging.warn('got collection with no samples')
        return
    g_t_t0 = g.t(collection.t0)
    w.log(g_t_t0, 'is_on', collection.extras['is_on'])

    v_mean_thing = MeanThing(50)
    j = None
    for sample in collection.samples:
        voltage = sample.item('/Robot/v').value
        j = sample.item('/Robot/pdb/j').value

        ts = sample.item('/Robot/hb').timestamp
        g_t_ts = g.t(ts)

        log_input_data(sample, w, g)

        v_mean_thing.add(voltage)
        v_mean = v_mean_thing.mean()
        soc = calculate_soc(v_mean)
        w.log(g_t_ts, '/analysis/v_noload', v_mean)
        w.log(g_t_ts, '/analysis/soc', soc)

        if g.soc_start is not None:
            g.soc_end = soc
            g.j_end = j
            w.log_float(g_t_ts, '/analysis/j_end', g.j_end)
            w.log_float(g_t_ts, '/analysis/soc_end', g.soc_end)

            soc_delta = g.soc_start - g.soc_end
            w.log_float(g_t_ts, '/analysis/soc_delta', soc_delta)
            if soc_delta > 0:
                j_delta = g.j_start - g.j_end
                capacity_estimate = -j_delta / soc_delta
                w.log_float(g_t_ts, '/analysis/j_delta', -j_delta)
                w.log_float(g_t_ts, '/analysis/capacity_estimate', capacity_estimate)

    soc = calculate_soc(v_mean)
    if g.soc_start is None and soc < 1.00:
        g.j_start = j  # shouldn't matter, j should not move during noload
        g.soc_start = soc
        w.log_float(g_t_ts, '/analysis/soc_start', g.soc_start)
        w.log_float(g_t_ts, '/analysis/j_start', g.j_start)

    g.v_noload = v_mean

    if g.v_load is not None:
        rint = (g.v_noload - g.v_load) / g.i_load
        w.log_float(g_t_ts, '/analysis/rint_reverse', rint)


def process_load(collection: BatteryDataSampleCollection, w: WPILogWriter, g: G = None):
    if not collection.extras['is_on']:
        raise ValueError()
    if len(collection.samples) == 0:
        logging.warn('got collection with no samples')
        return
    w.log(g.t(collection.t0), 'is_on', collection.extras['is_on'])
    v_mean_thing = MeanThing(50)
    i_mean_thing = MeanThing(50)
    for sample in collection.samples:
        log_input_data(sample, w, g)
        ts = sample.item('/Robot/hb').timestamp
        g_t_ts = g.t(ts)
        t_since_start = ts - collection.t0
        if g.v_noload is not None and t_since_start > 0.1:
            v = sample.item('/Robot/v').value
            v_drop = g.v_noload - v
            w.log(g_t_ts, '/analysis/v_drop', v_drop)

            v_mean_thing.add(v)
            v_drop_mean = g.v_noload - v_mean_thing.mean()
            w.log(g_t_ts, '/analysis/v_drop_mean', v_drop_mean)

            current = sample.total_heater_current()
            w.log(g_t_ts, '/analysis/current', current)
            i_mean_thing.add(current)
            w.log(g_t_ts, '/analysis/current_mean', i_mean_thing.mean())
            if current > 0:
                w.log(g_t_ts, '/analysis/rint', v_drop/current)
                w.log(g_t_ts, '/analysis/rint_mean', v_drop_mean/current)

    g.v_load = v_mean_thing.mean()
    g.i_load = i_mean_thing.mean()


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

    battery_id_item = None
    run_dt = None

    timestamp_at_first_on = None

    for sample in yield_samples_from_file(args.infile):
        setpoint = sample.item('/Robot/H/setpoint').value
        robot_mode = sample.item('/Robot/mode').value

        is_on = setpoint > 0 and robot_mode != 'DISABLED'
        if is_on and timestamp_at_first_on is None:
            timestamp_at_first_on = sample.item('/Robot/hb').timestamp
        if is_on != collection.extras['is_on']:
            collection = BatteryDataSampleCollection()
            collections.append(collection)
            collection.extras['is_on'] = is_on

        collection.add(sample)

        system_time = sample.item('systemTime')
        if system_time is not None and run_dt is None:
            start_time = (system_time.value / 1000000) - system_time.timestamp
            run_dt = datetime.datetime.fromtimestamp(start_time)
            logging.info("test started at %s", run_dt)

        battery_id_item = sample.item('/Robot/batteryId')

    if battery_id_item is None or battery_id_item.value == -1:
        raise ValueError("no /Robot/batteryId")

    if run_dt is None:
        raise ValueError("no systemTime")

    if args.output:
        outfile = args.output
    else:
        outfile = f'{os.path.dirname(args.infile)}/#{battery_id_item.value}_{run_dt.strftime("%Y%m%d-%H%M%S")}.wpilog'
    logging.info("writing %s", outfile)
    w = SmartWPILogWriter(outfile)

    g = G()
    g.t_offset = (- timestamp_at_first_on) + 10

    for collection in collections:
        is_on = collection.extras['is_on']
        if not is_on:
            process_no_load(collection, w=w, g=g)
        else:
            process_load(collection, w=w, g=g)

    w.log(0, '/analysis/valid', False)
    w.log(g.fake_t, '/analysis/valid', True)

    w.close()

    logging.info("processing took %s seconds", time.time() - t0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    main(sys.argv[1:])
