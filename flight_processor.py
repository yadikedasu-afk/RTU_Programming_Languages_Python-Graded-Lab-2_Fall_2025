import argparse
import csv
import json
from pathlib import Path
from datetime import datetime

""" 
python flight_processor.py -i db.csv
Name : Edasu Yadık
ID : 231AEB028

"""


def read_csv_rows(path):
    data = []
    with path.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            text = ",".join(row).strip()
            if not text or text.startswith("#"):
                continue
            data.append((text, row))
    return data

def valid_code(x):
    return len(x) == 3 and x.isalpha() and x.isupper()

def valid_id(x):
    return x.isalnum() and 2 <= len(x) <= 8

def valid_datetime(x):
    try:
        return datetime.strptime(x, "%Y-%m-%d %H:%M")
    except:
        return None

def valid_price(x):
    try:
        v = float(x)
        return v if v > 0 else None
    except:
        return None

def evaluate_row(raw, fields):
    if len(fields) != 6:
        return None, "incorrect number of fields"

    fid, org, dst, dep, arr, pr = [x.strip() for x in fields]

    if not valid_id(fid):
        return None, "invalid flight_id"

    if not valid_code(org):
        return None, "invalid origin code"

    if not valid_code(dst):
        return None, "invalid destination code"

    d1 = valid_datetime(dep)
    if not d1:
        return None, "invalid departure datetime"

    d2 = valid_datetime(arr)
    if not d2:
        return None, "invalid arrival datetime"

    if d2 <= d1:
        return None, "arrival must be after departure"

    p = valid_price(pr)
    if p is None:
        return None, "invalid price value"

    return {
        "flight_id": fid,
        "origin": org,
        "destination": dst,
        "departure_datetime": dep,
        "arrival_datetime": arr,
        "price": p
    }, ""

def process_file(path):
    rows = read_csv_rows(path)
    good = []
    bad = []
    for raw, fields in rows:
        record, msg = evaluate_row(raw, fields)
        if record is None:
            bad.append(f"{path.name}: {raw} => {msg}")
        else:
            good.append(record)
    return good, bad

def collect_csv(path):
    return sorted([p for p in path.iterdir() if p.suffix.lower() == ".csv"])

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i")
    group.add_argument("-d")
    parser.add_argument("-o")
    args = parser.parse_args()

    csv_list = []

    if args.i:
        csv_list = [Path(args.i)]
    else:
        folder = Path(args.d)
        csv_list = collect_csv(folder)

    all_good = []
    all_bad = []

    for f in csv_list:
        g, b = process_file(f)
        all_good.extend(g)
        all_bad.extend(b)

    out_json = Path(args.o) if args.o else Path("db.json")
    out_err = out_json.with_name("errors.txt")

    with out_json.open("w", encoding="utf-8") as f:
        json.dump(all_good, f, indent=4)

    with out_err.open("w", encoding="utf-8") as f:
        if all_bad:
            f.write("\n".join(all_bad) + "\n")
        else:
            f.write("")

if __name__ == "__main__":
    main()
