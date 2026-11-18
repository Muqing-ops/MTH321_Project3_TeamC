"""Build a space-time panel of (density, flow, speed) from NGSIM trajectories.

Provided utility, not an assessed deliverable.  It converts the downloaded
vehicle-trajectory slice into the one-dimensional quantities the Lighthill--
Whitham--Richards (LWR) form ``rho_t + q(rho)_x = 0`` needs, using Edie's
generalised definitions over a cell ``[x0, x0+dx) x [t0, t0+dt)``:

    k = sum_i dt_i                 / (dx * dt)      vehicles per unit length
    q = sum_i v_i * dt_i           / (dx * dt)      vehicles per unit time
    v = q / k                                        space-mean speed

Each trajectory sample stands for the time step ``dt_i`` that follows it, so
its contribution to distance travelled is ``v_i * dt_i``.  Both quantities are
credited to the cell containing the vehicle at that instant.  A vehicle step
moves a few feet while ``dx`` is tens of feet, so the boundary misassignment
is small; it is not zero, and it is the reason the panel is a discretisation of
the data rather than a definition of it.  State ``dx`` and ``dt`` whenever you
report a number taken from the panel.

Units in the raw file are NGSIM's: ``local_y`` in feet along the section,
``v_vel`` in feet per second, ``global_time`` in milliseconds since the epoch.
The panel reports ``k`` in vehicles per mile, ``q`` in vehicles per hour and
``v`` in miles per hour, because that is how traffic data are quoted.

Usage
-----
    python build_panel.py RAW.csv PANEL.csv [--dx 50] [--dt 10] [--lanes 1,2,3,4,5,6]

``--lanes`` keeps only the listed ``lane_id`` values.  The published I-80 record
has six through lanes (1--6) and one on-ramp lane (7) that exists over only part
of the section; include it only when you want to show what the merge does.

The input needs the columns ``vehicle_id``, ``frame_id``, ``global_time``,
``local_y``, ``lane_id`` and ``v_vel``.  Rows whose speed or position are
missing are dropped and counted; the script prints what it dropped so the
loss is visible instead of silent.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import defaultdict

FT_PER_MILE = 5280.0
SEC_PER_HOUR = 3600.0
DEFAULT_DT_SAMPLE = 0.1  # NGSIM sampling interval, seconds


def read_rows(path, lanes=None):
    """Return per-vehicle samples, sorted, with the sampling step per vehicle."""
    per_vehicle = defaultdict(list)
    dropped = 0
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            try:
                vid = row["vehicle_id"]
                t = int(row["global_time"])
                x = float(row["local_y"])
                v = float(row["v_vel"])
            except (KeyError, TypeError, ValueError):
                dropped += 1
                continue
            if v < 0.0 or x < 0.0:  # negative speeds are NGSIM noise, not flow
                dropped += 1
                continue
            lane = row.get("lane_id", "")
            if lanes is not None and lane.strip() not in lanes:
                continue
            per_vehicle[vid].append((t, x, v, lane))
    for samples in per_vehicle.values():
        samples.sort()
    return per_vehicle, dropped


def sampling_step(per_vehicle):
    """Median gap between consecutive samples, in seconds."""
    gaps = []
    for samples in per_vehicle.values():
        for a, b in zip(samples, samples[1:]):
            gaps.append((b[0] - a[0]) / 1000.0)
    if not gaps:
        return DEFAULT_DT_SAMPLE
    return statistics.median(gaps)


def build_panel(per_vehicle, dx_ft, dt_s, dt_sample):
    """Accumulate Edie averages on a regular (x, t) grid."""
    pres = defaultdict(float)   # sum of dt_i
    dist = defaultdict(float)   # sum of v_i * dt_i
    count = defaultdict(int)
    vehicles = defaultdict(set)
    t_origin = min(s[0][0] for s in per_vehicle.values())

    for vid, samples in per_vehicle.items():
        for t, x, v, _lane in samples:
            ti = int((t - t_origin) / 1000.0 // dt_s)
            xi = int(x // dx_ft)
            pres[(ti, xi)] += dt_sample
            dist[(ti, xi)] += v * dt_sample
            count[(ti, xi)] += 1
            vehicles[(ti, xi)].add(vid)

    rows = []
    for (ti, xi) in sorted(pres):
        area = dx_ft * dt_s
        k_per_ft = pres[(ti, xi)] / area
        q_per_s = dist[(ti, xi)] / area
        k = k_per_ft * FT_PER_MILE
        q = q_per_s * SEC_PER_HOUR
        rows.append(
            {
                "t_start_s": ti * dt_s,
                "x_start_ft": xi * dx_ft,
                "k_veh_per_mile": k,
                "q_veh_per_hour": q,
                "v_space_mph": (q / k) if k > 0 else float("nan"),
                "n_samples": count[(ti, xi)],
                "n_vehicles": len(vehicles[(ti, xi)]),
            }
        )
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("raw", help="trajectory CSV")
    ap.add_argument("panel", help="output panel CSV")
    ap.add_argument("--dx", type=float, default=50.0, help="cell length, ft")
    ap.add_argument("--dt", type=float, default=10.0, help="cell duration, s")
    ap.add_argument("--lanes", default="", help='comma-separated lane_id values, e.g. "1,2,3,4,5,6"; default all')
    args = ap.parse_args(argv)

    lanes = {s.strip() for s in args.lanes.split(",") if s.strip()} or None
    per_vehicle, dropped = read_rows(args.raw, lanes)
    if not per_vehicle:
        sys.exit("no usable rows in %s" % args.raw)

    dt_sample = sampling_step(per_vehicle)
    rows = build_panel(per_vehicle, args.dx, args.dt, dt_sample)

    with open(args.panel, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in row.items()})

    t_span = max(s[-1][0] for s in per_vehicle.values()) - min(s[0][0] for s in per_vehicle.values())
    lane_note = "all lanes" if lanes is None else "lanes " + ",".join(sorted(lanes))
    print(f"vehicles {len(per_vehicle)}, samples {sum(len(s) for s in per_vehicle.values())}, dropped {dropped}, {lane_note}")
    print(f"sampling step {dt_sample:.3f} s, span {t_span/1000.0:.1f} s")
    print(f"grid dx {args.dx:g} ft x dt {args.dt:g} s -> {len(rows)} cells -> {args.panel}")
    speeds = [r["v_space_mph"] for r in rows if r["k_veh_per_mile"] > 0]
    if speeds:
        print(f"space-mean speed over occupied cells: median {statistics.median(speeds):.1f} mph, "
              f"range {min(speeds):.1f}-{max(speeds):.1f} mph")


if __name__ == "__main__":
    main()
