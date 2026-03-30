import logging
import struct
import sys

doubleStruct = struct.Struct("<d")

class WPILogWriter:
    def __init__(self, filename : str = None):
        self.fp = open(filename, 'wb')
        self.entry_ids = {}
        self.entry_types = {}
        self.next_entry_id = 1
        self.logger = logging.getLogger("WPILogWriter")

        self.write_file_header()


    def write_file_header(self):
        ba = bytearray()
        ba.extend(b'WPILOG')
        ba.extend(0x0100.to_bytes(2, byteorder='little', signed=False))
        ba.extend((0).to_bytes(length=4, byteorder='little', signed=False))

        self.logger.debug("Writing header '%s' %d", ba, len(ba))

        self.fp.write(ba)

    def close(self):
        self.fp.close()

    def write_record(self, entry_id : int = None, timestamp : float = None, payload: bytes | bytearray = None):
        if timestamp < 0:
            return
        ba = bytearray()
        ba.append(0b00110101)   # 4 byte timestamp length, 2 byte payload size, 2 byte entry id size
        ba.extend(entry_id.to_bytes(length=2, byteorder='little', signed=False))
        ba.extend(len(payload).to_bytes(length=2, byteorder='little', signed=False))
        timestamp_micros = int(timestamp * 1000000)
        ba.extend(timestamp_micros.to_bytes(length=4, byteorder='little', signed=False))
        ba.extend(payload)
        self.logger.debug("Payload '%s' %d", payload, len(payload))
        self.logger.debug("Writing record '%s' %d", ba, len(ba))
        self.fp.write(ba)


    def write_start(self, entry_id : int = None, timestamp : float = None, entry_name : str = None, entry_type = None):
        payload = bytearray()
        payload.append(0)       # 0 = start control record
        payload.extend(entry_id.to_bytes(length=4, byteorder='little', signed=False))
        entry_name_utf8 = entry_name.encode('utf-8')
        payload.extend(len(entry_name_utf8).to_bytes(length=4, byteorder='little', signed=False))
        payload.extend(entry_name_utf8)
        entry_type_utf8 = entry_type.encode('utf-8')
        payload.extend(len(entry_type_utf8).to_bytes(length=4, byteorder='little', signed=False))
        payload.extend(entry_type_utf8)
        payload.extend(b'\x00\x00\x00\x00')     # zero length metadata
        self.write_record(0, timestamp, payload)

    def find_entry_id(self, timestamp : float = None, name : str = None, entry_type : str = None):
        entry_id = self.entry_ids.get(name)
        if entry_id is None:
            entry_id = self.next_entry_id
            self.entry_ids[name] = entry_id
            self.entry_types[name] = entry_type
            self.next_entry_id += 1

            self.write_start(entry_id, timestamp, name, entry_type)
        else:
            existing_entry_type = self.entry_types.get(name)
            if entry_type != existing_entry_type:
                raise Exception()

        return entry_id

    def log_string(self, timestamp : float = None, name : str = None, value : str = None):
        entry_id = self.find_entry_id(timestamp=timestamp, name=name, entry_type='string')
        self.write_record(entry_id, timestamp, value.encode('utf-8'))

    def log_int(self, timestamp : float = None, name : str = None, value : int = None):
        entry_id = self.find_entry_id(timestamp=timestamp, name=name, entry_type='int64')
        self.write_record(entry_id, timestamp, value.to_bytes(length=8, byteorder='little', signed=True))

    def log_float(self, timestamp : float = None, name : str = None, value : float = None):
        entry_id = self.find_entry_id(timestamp=timestamp, name=name, entry_type='double')
        self.write_record(entry_id, timestamp, doubleStruct.pack(value))

    def log_boolean(self, timestamp : float = None, name : str = None, value : bool = None):
        entry_id = self.find_entry_id(timestamp=timestamp, name=name, entry_type='boolean')
        self.write_record(entry_id, timestamp, b'\x01' if value else b'\x00')

    def log(self, timestamp : float = None, name : str = None, value = None):
        if type(value) == int:
            self.log_int(timestamp, name, value)
        elif type(value) == float:
            self.log_float(timestamp, name, value)
        elif type(value) == str:
            self.log_string(timestamp, name, value)
        elif type(value) == bool:
            self.log_boolean(timestamp, name, value)
        else:
            raise TypeError(f"tried to log value '{value}' of type {type(value)} to '{name}'")


class SmartWPILogWriter(WPILogWriter):
    def __init__(self, filename: str = None):
        super().__init__(filename = filename)
        self.last_timestamps = {}

    def log(self, timestamp : float = None, name : str = None, value = None):
        last_timestamp = self.last_timestamps.get(name)
        if last_timestamp is None or timestamp > last_timestamp:
            super().log(timestamp, name, value)
        self.last_timestamps[name] = timestamp


def main(argv):
    w = WPILogWriter('test.wpilog')
    """
    w.log_string(0.001, 'str', 'str_value')
    w.log_string(1, 'str', 'str_value2')
    w.log_int(0, 'i', 0)
    w.log_int(1, 'i', -1)
    w.log_int(2, 'i', +1)
    w.log_float(.500000, 'f', 0.5)
    w.log_float(1.000000, 'f', 1.0)
    w.log_float(1.500000, 'f', -1.0)
    """
    w.log_boolean(.500000, 'b', False)
    w.log_boolean(1.000000, 'b', True)
    w.log_boolean(1.500000, 'b', False)

    w.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
    main(sys.argv[1:])