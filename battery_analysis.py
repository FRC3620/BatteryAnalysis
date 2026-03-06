import logging
import pickle
import re
import sys

from typing import List, Self, Dict

from datalog import DataLogReader


class BatteryDataItem:
    def __init__(self, name=None, timestamp=None, value=None):
        self.name = name
        self.timestamp = timestamp
        self.value = value

    def __str__(self):
        return f'{self.name} = {self.value} @ {self.timestamp}'


def yield_from_datalog(filename : str = None):
    """

    :param filename:
    :return: yields tuples of timestamp, name, value, data type, and raw data
    """
    import mmap
    from datetime import datetime

    with open(filename, "r") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        reader = DataLogReader(mm)
        if not reader:
            logging.error("not a log file")
            sys.exit(1)

        entries = {}
        for record in reader:
            timestamp = record.timestamp / 1000000
            if record.isStart():
                try:
                    data = record.getStartData()
                    logging.debug(f"Start({data.entry}, name='{data.name}', type='{data.type}', metadata='{data.metadata}') [{timestamp}]")
                    if data.entry in entries:
                        # TODO
                        logging.warning("...DUPLICATE entry ID, overriding")
                    entries[data.entry] = data
                except TypeError:
                    logging.error("Start(INVALID)")
            elif record.isFinish():
                try:
                    entry = record.getFinishEntry()
                    logging.debug(f"Finish({entry}) [{timestamp}]")
                    if entry not in entries:
                        # TODO
                        logging.warning("...ID not found")
                    else:
                        del entries[entry]
                except TypeError:
                    logging.error("Finish(INVALID)")
            elif record.isSetMetadata():
                try:
                    data = record.getSetMetadataData()
                    logging.debug(f"SetMetadata({data.entry}, '{data.metadata}') [{timestamp}]")
                    if data.entry not in entries:
                        # TODO
                        logging.warning("...ID not found")
                except TypeError:
                    logging.error("SetMetadata(INVALID)")
            elif record.isControl():
                logging.error("Unrecognized control record")
            else:
                logging.debug(f"Data({record.entry}, size={len(record.data)}) ")
                entry = entries.get(record.entry)
                if entry is None:
                    logging.warning("<ID not found>")
                    continue
                logging.debug(f"<name='{entry.name}', type='{entry.type}'> [{timestamp}]")

                try:
                    rv = None
                    rt = entry.type
                    # handle systemTime specially
                    if entry.name == "systemTime" and entry.type == "int64":
                        rv = datetime.fromtimestamp(record.getInteger() / 1000000)
                        rt = "DATETIME"
                        # print("  {:%Y-%m-%d %H:%M:%S.%f}".format(dt))

                    elif entry.type == "double":
                        rv = record.getDouble()
                    elif entry.type == "int64":
                        rv = record.getInteger()
                    elif entry.type in ("string", "json"):
                        rv = record.getString()
                    elif entry.type == "msgpack":
                        rv = record.getMsgPack()
                    elif entry.type == "boolean":
                        rv = record.getBoolean()
                    elif entry.type == "boolean[]":
                        rv = record.getBooleanArray()
                    elif entry.type == "double[]":
                        rv = record.getDoubleArray()
                    elif entry.type == "float[]":
                        rv = record.getFloatArray()
                    elif entry.type == "int64[]":
                        rv = record.getIntegerArray()
                    elif entry.type == "string[]":
                        rv = record.getStringArray()
                    battery_data_item = BatteryDataItem(name=entry.name, timestamp=timestamp, value=rv)
                    yield battery_data_item, rt, record.data
                except TypeError:
                    logging.error ("got a TypeError")


class SlidingWindowMean:
    def __init__(self, l=50):
        self.v = []
        self.l = l

    def mean(self, v):
        self.v.append(v)
        if len(self.v) > self.l:
            del self.v[0]
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
        self.battery_data_items : Dict[str, BatteryDataItem] = {}
        self.timestamp = None
        if template is not None:
            self.battery_data_items = template.battery_data_items.copy()
            self.timestamp = template.timestamp

    def add(self, battery_data_item : BatteryDataItem):
        self.battery_data_items[battery_data_item.name] = battery_data_item

    def items(self):
        for battery_data_item in self.battery_data_items:
            yield battery_data_item

    def items_matching(self, pattern):
        regexp = re.compile(pattern)
        for name, battery_data_item in self.battery_data_items.items():
            if regexp.fullmatch(name):
                yield battery_data_item

    def item(self, name : str = None) -> BatteryDataItem:
        return self.battery_data_items.get(name)

    def total_heater_current(self):
        rv = 0
        for battery_data_item in self.items_matching(r'/Robot/H\d+/input/a'):
            rv += battery_data_item.value
        return rv


def yield_samples_from_datalog(filename : str = None):
    """

    :param filename: name of the file to read from
    :return:
    """
    rv = BatteryDataSample()
    for t in yield_from_datalog(filename):
        battery_data_item, _, _ = t
        rv.add(battery_data_item)
        if battery_data_item.name == '/Robot/hb':
            rv.timestamp = battery_data_item.timestamp
            yield BatteryDataSample(rv)

def yield_samples_from_pickle(filename : str = None):
    with open(filename, 'rb') as fp:
        samples = pickle.load(fp)
        for sample in samples:
            yield(sample)

def yield_samples_from_file(filename : str = None):
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
    sm = SlidingWindowMean(l=100)
    in_a_row = ConsecutiveLT(n=9, threshold=threshold)
    for battery_data_sample in yield_samples_from_datalog('data/FRC_20260305_005905.wpilog'):
        robot_v = battery_data_sample.item('/Robot/v')
        vv = robot_v.value
        slm = sm.mean(vv)
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
