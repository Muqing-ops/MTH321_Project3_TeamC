"""Download the one-second I-80 teaching extract from the U.S. DOT DataHub."""

import csv
import io
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


ENDPOINT = "https://data.transportation.gov/resource/8ect-6jqj.csv"
OUTPUT = Path("ngsim_i80_2005-04-13_1600-1615_raw_1s.csv")
COLUMNS = ("vehicle_id", "frame_id", "global_time", "local_y", "lane_id", "v_vel", "v_class")
START_MS = 1113433200000
END_MS = 1113434100000
STEP_MS = 1000
BATCH_MS = 60 * STEP_MS
PAGE_SIZE = 50000
EXPECTED_ROWS = 122661


def download_rows():
    rows = []
    for start in range(START_MS, END_MS, BATCH_MS):
        end = min(start + BATCH_MS, END_MS)
        timestamps = ",".join(map(str, range(start, end, STEP_MS)))
        query = {
            "$select": ",".join(COLUMNS),
            "$where": f"location='i-80' AND global_time IN ({timestamps})",
            "$order": ":id",
            "$limit": PAGE_SIZE,
            "$offset": 0,
        }
        while True:
            with urlopen(f"{ENDPOINT}?{urlencode(query)}", timeout=90) as response:
                with io.TextIOWrapper(response, encoding="utf-8-sig", newline="") as stream:
                    reader = csv.reader(stream)
                    if next(reader, None) != list(COLUMNS):
                        raise ValueError("Unexpected CSV header from the U.S. DOT DataHub.")
                    page = list(reader)
            rows.extend(page)
            if len(page) < PAGE_SIZE:
                break
            query["$offset"] += PAGE_SIZE
        print(f"Downloaded {(end - START_MS) // STEP_MS} of 900 seconds", flush=True)
    return rows


def row_key(row):
    return int(row[2]), int(row[0])


def main():
    if OUTPUT.exists():
        raise SystemExit(f"{OUTPUT} already exists. Move it before downloading a fresh copy.")

    try:
        rows = download_rows()
        keys = {row_key(row) for row in rows}
        timestamps = {timestamp for timestamp, _ in keys}
        if (
            len(rows) != EXPECTED_ROWS
            or len(keys) != EXPECTED_ROWS
            or timestamps != set(range(START_MS, END_MS, STEP_MS))
            or any(len(row) != len(COLUMNS) for row in rows)
        ):
            raise ValueError(f"Expected {EXPECTED_ROWS:,} unique samples over 900 seconds, got {len(rows):,} rows.")

        with OUTPUT.open("x", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(COLUMNS)
            writer.writerows(sorted(rows, key=row_key))
    except (OSError, ValueError, IndexError, csv.Error) as error:
        raise SystemExit(f"Could not save the I-80 extract. {error}") from error

    print(f"Saved {len(rows):,} trajectory rows to {OUTPUT}")


if __name__ == "__main__":
    main()
