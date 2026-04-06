import argparse
import csv
import glob
import json
import logging
import re
import sys
import unicodedata

def sanitize_name(name):
    rv = "".join(ch if unicodedata.category(ch)[0] != "C" else " " for ch in name)
    rv = rv.strip()
    rv = " ".join(rv.split())  # collapse multiple spaces into singles
    print(name, rv)
    return rv


def vvvv(s):
    m = re.match(r'^(\d+)%$', s)
    if m:
        return float(m.group(1))
    return s


def read_sheet_rows_csv(file):
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i == 0:
                names = [sanitize_name(name) for name in row]
            else:
                row_dict = dict(zip(names, [vvvv(s) for s in row]))
                yield row_dict


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--output', '-o')
    parser.add_argument('--google-sheet', '-g')
    parser.add_argument('inglob', nargs='+')
    args = parser.parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    db = {}
    for row in read_sheet_rows_csv(args.google_sheet):
        print(row)
        db_key = f"{row.get('Battery Id')}-{row.get('Date/time')}"
        if db_key != "-":
            db[db_key] = row
    # print(json.dumps(db, indent=1, default=str))

    field_names = set()

    for inglob1 in args.inglob:
        for infile in glob.glob(inglob1):
            with open(infile, 'rb') as f:
                td = json.load(f)
                db_key = f"{td['battery_id']}-{td['start_time']}"
                row = db.get(db_key)
                if row is not None:
                    row.update(td)
                    row['analyzed'] = True
                    row['test_name'] = f"{td['battery_id']} {td['start_time']}"
                    field_names.update(row.keys())
                else:
                    logging.warning("cannot find %s", db_key)

    # print(json.dumps(db, indent=1, default=str))

    field_names.add("sequence")
    field_names.add("test_name")
    field_names.add("position")

    with open('rollup.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)

        writer.writeheader()
        seq = 0
        position = 0
        last_battery_id = None
        for k, v in sorted(db.items(), key=lambda v: v[0]):
            if not v.get('analyzed', False):
                continue
            battery_id = v['battery_id']
            if battery_id != last_battery_id:
                seq = 0
            else:
                seq += 1
            last_battery_id = battery_id
            v['sequence'] = seq
            v['position'] = position
            position += 1
            writer.writerow(v)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    main(sys.argv[1:])
