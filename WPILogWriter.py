import logging
import struct
import sys

doubleStruct = struct.Struct("<d")

kControlStart = 0
kControlFinish = 1
kControlSetMetadata = 2

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
        ba.extend(b'\x00\x00\x00\x00')

        self.logger.debug("Writing header '%s' %d", ba, len(ba))

        self.fp.write(ba)

    def close(self):
        self.fp.close()

    def write_record(self, entry_id : int = None, timestamp : int = None, payload: bytes | bytearray = None):
        ba = bytearray()
        ba.append(0b00110101)   # 4 byte timestamp length, 2 byte payload size, 2 byte entry id size
        ba.extend(entry_id.to_bytes(length=2, byteorder='little', signed=False))
        ba.extend(len(payload).to_bytes(length=2, byteorder='little', signed=False))
        ba.extend(timestamp.to_bytes(length=4, byteorder='little', signed=False))
        ba.extend(payload)
        self.logger.debug("Writing record '%s' %d", ba, len(ba))
        self.fp.write(ba)


    def write_start(self, entry_id : int = None, timestamp : int = None, entry_name : str = None, entry_type = None):
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

    def log_string(self, timestamp : int = None, name : str = None, value : str = None):
        my_entry_type = 'string'
        entry_id = self.entry_ids.get(name)
        if entry_id is None:
            entry_id = self.next_entry_id
            self.entry_ids[name] = entry_id
            self.entry_types[name] = my_entry_type
            self.next_entry_id += 1

            self.write_start(entry_id, timestamp, name, my_entry_type)
        else:
            entry_type = self.entry_types.get(name)
            if entry_type != my_entry_type:
                raise Exception()

        self.write_record(entry_id, timestamp, value.encode('utf-8'))

    def log_int(self, timestamp : int = None, name : str = None, value : int = None):
        my_entry_type = 'int64'
        entry_id = self.entry_ids.get(name)
        if entry_id is None:
            entry_id = self.next_entry_id
            self.entry_ids[name] = entry_id
            self.entry_types[name] = my_entry_type
            self.next_entry_id += 1

            self.write_start(entry_id, timestamp, name, my_entry_type)
        else:
            entry_type = self.entry_types.get(name)
            if entry_type != my_entry_type:
                raise Exception()

        self.write_record(entry_id, timestamp, value.to_bytes(length=8, byteorder='little', signed=True))



def main(argv):
    w = WPILogWriter('test.wpilog')
    w.log_string(1000, 'str', 'str_value')
    w.log_string(1000000, 'str', 'str_value2')
    w.log_int(0, 'i', 0)
    w.log_int(1000000, 'i', -1)
    w.log_int(2000000, 'i', +1)

    w.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
    main(sys.argv[1:])