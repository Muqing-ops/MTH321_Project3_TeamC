# `07_Data` — I-80 trajectory extract (NGSIM)

Download and preparation instructions for the *I-80 Emeryville: diagnosing congestion
waves* case. The student pack supplies the two Python scripts below. They retrieve the
trajectory subset directly from the U.S. DOT DataHub and build the analysis panel locally.

## Download and build

Open a terminal in the extracted `07_Data` folder and run these two commands. Both scripts
use the Python 3 standard library. Use `python3` in place of `python` if that is how your
system starts Python 3. The download needs an internet connection and no account.

```sh
python download_i80.py
python build_panel.py ngsim_i80_2005-04-13_1600-1615_raw_1s.csv ngsim_i80_2005-04-13_1600-1615_panel_through.csv --dx 50 --dt 10 --lanes 1,2,3,4,5,6
```

The first command requests only the seven listed fields at whole-second timestamps for
eastbound I-80, 13 April 2005, 23:00–23:15 UTC. Expect **122,661 trajectory rows** from
2,052 vehicles (about 5 MB on disk). The second command should report a **1.000 s** sampling
step and **3,007 occupied cells**. Record your access date and keep the downloaded CSV
with your query and grid settings so you can reproduce the analysis.

## Source and licence

| | |
| --- | --- |
| Dataset | Next Generation Simulation (NGSIM) Vehicle Trajectories and Supporting Data |
| Agency | U.S. Department of Transportation, Federal Highway Administration (FHWA), ITS Joint Program Office |
| DOI | [10.21949/1504477](https://doi.org/10.21949/1504477) |
| Portal | [datahub.transportation.gov, dataset `8ect-6jqj`](https://datahub.transportation.gov/d/8ect-6jqj) |
| Site description | [FHWA-HRT-06-137, *Interstate 80 Freeway Dataset*](https://www.fhwa.dot.gov/publications/research/operations/06137/) |
| Licence | [Creative Commons Attribution–ShareAlike 3.0 Unported (CC BY-SA 3.0)](https://creativecommons.org/licenses/by-sa/3.0/legalcode), as listed in the [federal catalogue](https://catalog.data.gov/dataset/next-generation-simulation-ngsim-vehicle-trajectories-and-supporting-data) |
| Reference extract accessed | 2026-11-04 |
| Required citation | U.S. Department of Transportation Federal Highway Administration. (2016). *Next Generation Simulation (NGSIM) Vehicle Trajectories and Supporting Data.* [Dataset]. Provided by ITS JPO DataHub. |

The two CSVs produced by this workflow are adaptations of the FHWA data under CC BY-SA
3.0. Keep this source and licence notice with redistributed copies and adaptations.

The `i-80` site is **eastbound** Interstate 80 in Emeryville, California. The FHWA fact
sheet gives a study area of about 500 m (1,640 ft) with six freeway lanes and the Powell
Street on-ramp inside it; the published coordinates run to about 1,752 ft, and seven
`lane_id` values appear in the record because the on-ramp lane is numbered separately.
Trajectories were recorded at 0.1 s. The documentation attached to the portal record
(`I-80_Metadata_Documentation.pdf`) defines the coordinate system, the recording setup
and the data-processing history; note that its own label for the direction is not
consistent, which is why the FHWA fact sheet is cited for it here.

## What was extracted

The **nominal 4:00–4:15 p.m. period**, taken as the half-open interval
`global_time ≥ 1113433200000` and `< 1113434100000`: exactly 2005-04-13
23:00:00–23:15:00 UTC, or 16:00:00–16:15:00 PDT (UTC−7). Half-open matters here: it
keeps 900 whole seconds, so every 10 s cell of the panel is complete. Including the
endpoint instant instead adds a 91st time column holding one second of data divided by
ten, which reads as a spurious drop in density and flow.

Two clocks are in play and they do not agree exactly. The epoch numbers above are what
the record contains and what to quote. The period *label* is 4:00–4:15 p.m., and the same
period's record also holds rows from 22:58:55 to 23:15:36 UTC — outside the nominal
quarter hour. The script selects the nominal quarter hour.

The published half-open window holds **1,226,650 native rows** (verified against
`count(*)` on the same `$where` clause). The teaching extract samples at 1 s —
every sample whose `global_time` is a whole second — which leaves 122,661 rows and 2,052
vehicles.

| File | Rows | Sampling | Purpose |
| --- | --- | --- | --- |
| `ngsim_i80_2005-04-13_1600-1615_raw_1s.csv` | 122,661 | 1 s | build your own panel, plot trajectories, test your own definition |
| `ngsim_i80_2005-04-13_1600-1615_panel_through.csv` | 3,007 | 50 ft × 10 s cells | the aggregated $(k,q,v)$ product, six through lanes, ready to use |

`raw_1s.csv` columns: `vehicle_id, frame_id, global_time, local_y, lane_id, v_vel, v_class`.
Units are NGSIM's: distance in feet along the section (increasing in the direction of
travel, so downstream), speed in ft/s, `global_time` in milliseconds since the Unix epoch.
`v_class` is 1 = motorcycle, 2 = car, 3 = truck. Request `local_x` (lateral offset within
the section) and `v_acc` from the source if your analysis needs those fields.

`panel_through.csv` columns: `t_start_s, x_start_ft, k_veh_per_mile, q_veh_per_hour,
v_space_mph, n_samples, n_vehicles`. `n_samples` counts trajectory samples in the cell, so
its meaning depends on the sampling interval; the presence it represents is
$n_{\text{samples}}\times\Delta t_{\text{sample}}$ — for example, 30 vehicle-seconds
corresponds to 30 samples at 1 s or 300 at the native 0.1 s. This threshold selects on
density as well as sample support, so it is not neutral; see the sensitivity discussion below.
`k` and `q` aggregate lanes 1–6; per-lane values are roughly $k/6$ but not exactly,
because lane assignment is not fixed. The last spatial column, $x=1750$ ft, covers only the
2.4 ft between 1,750 ft and the 1,752.4 ft of published coordinates: it is a partial cell
(one cell in the whole panel), so drop it or say you kept it.

## How the panel was built

Edie's generalised definitions over a cell $[x_0,x_0+\Delta x)\times[t_0,t_0+\Delta t)$:

$$k=\frac{1}{\Delta x\,\Delta t}\sum_i \Delta t_i,\qquad
  q=\frac{1}{\Delta x\,\Delta t}\sum_i v_i\,\Delta t_i,\qquad
  v=\frac{q}{k}.$$

Each sample stands for the step $\Delta t_i$ that follows it, so its contribution to distance
is $v_i\Delta t_i$. Both are credited to the cell containing the vehicle at that instant; a
vehicle moves a few feet per step against $\Delta x=50$ ft, so the boundary misassignment is
small but not zero. This is a discretisation of the data, not a definition of it — always
state $\Delta x$, $\Delta t$ and the presence threshold with any number you take from the panel.

Drop `--lanes` and lane 7, the on-ramp lane, is included; it exists over only 282–666 ft of
the section, so including it raises density on that stretch and changes the peak flow and
the fitted slope (numbers below). Run both if you want to say what the merge does.

## Reference values (for checking your own pipeline)

Measured on `panel_through.csv` with a 30 vehicle-second threshold and, for the
fundamental diagram, 25 veh/mi bins of the median $q$ (bins with fewer than five cells
dropped):

- 2,633 of 3,007 cells survive the threshold. The median $n_{\text{samples}}$ is 42
  in the retained cells and 41 across all cells;
- median space-mean speed **18.2 mph**, range 4.3–31.1 mph over surviving cells;
- the largest retained binned median is near $k\approx425$ veh/mi (about 71 per through
  lane) at $q\approx8{,}350$ veh/h; this is conditional on the filter, not necessarily the
  peak of the full fundamental diagram;
- 154 cells have $k<100$ veh/mi, but none survives this filter. Their exclusion follows
  from the threshold itself and does not establish whether free flow was observed;
- slopes from binned medians over the ranges shown; ranges beginning below 425 veh/mi
  include bins below the retained peak:

  | fitted over | bins | slope | $r^2$ |
  | --- | --- | --- | --- |
  | $k\ge300$ | 20 | −5.93 ft/s (−4.04 mph) | 0.715 |
  | $k\ge350$ | 18 | −7.61 ft/s (−5.19 mph) | 0.880 |
  | $k\ge400$ | 16 | −9.07 ft/s (−6.18 mph) | 0.958 |
  | $k\ge425$ | 15 | −9.48 ft/s (−6.46 mph) | 0.964 |
  | $k\ge450$ | 14 | −9.74 ft/s (−6.64 mph) | 0.963 |
  | $k\ge475$ | 13 | −10.17 ft/s (−6.93 mph) | 0.967 |

  The slope moves by a factor of two across these ranges, which is why the fitted range is
  part of the answer and not a footnote. It is also a property of the closure you fitted:
  it estimates the characteristic speed that $q(\rho)$ implies, not a speed you measured.

Including lane 7 (all-lane panel, same threshold and bins): peak $q\approx8{,}490$ veh/h at
$k\approx425$, and the slope over $k\ge425$ is −7.79 ft/s (−5.31 mph), $r^2=0.905$.

Those numbers are a sanity check, not a target. Yours will differ with $\Delta x$, $\Delta t$,
the threshold, the bin width and the fitted range — which is exactly why all four are stated.

## Limitations you must state in the report

1. **The presence filter selects on density.** Here
   $k=(5280/(50\times10))\,\text{presence}=10.56\,\text{presence}$ veh/mi when presence
   is in vehicle-seconds. The 30 vehicle-second threshold therefore excludes every cell
   below 316.8 veh/mi by construction: 374 of the 3,007 cells, including all 154 below
   100 veh/mi. Compare the scatter and peak under lower thresholds, or recompute with
   different cell sizes, and discuss the trade-off between selection and noisy, sparsely
   sampled cells. Do not infer the absence of free flow from the filtered plot. A fitted
   slope is not a measured wave or shock; an observed shock claim needs independent
   space–time evidence of the states and their propagation.
2. **It is a 1 s product.** The native record is 0.1 s; decimation keeps 10 % of the
   samples, but each retained sample represents ten times as long. Estimated presence is
   therefore approximately preserved, not reduced tenfold; individual cells can differ
   through sampling and boundary assignment, and the 1 s panel may be noisier. Thresholds
   stated as sample counts do not survive a change of resolution; state them in
   vehicle-seconds. The source also provides native resolution (see below); the previously computed
   binned peak and slope agree to within a few per cent for the stated choices.
3. **A 900 s window is short.** Slow drift over 15 min is not a stationary state; any
   steady-state assumption needs a stationarity check on the panel itself.
4. **Multi-lane aggregation loses the lane structure**, and the section contains a merge, so
   the one-dimensional reduction is an approximation (see the situation's integrity guardrails).
5. **The record is from 2005 and is a research instrument**, not an operational feed: vehicle
   classification, missing samples and processing history all enter the numbers.
6. **Share-alike**: a published derivative of these files must carry the same licence and the
   citation above.

## API query for optional native-resolution analysis

The CSV endpoint is
[`data.transportation.gov/resource/8ect-6jqj.csv`](https://data.transportation.gov/resource/8ect-6jqj.csv).
The supplied downloader queries whole-second timestamps in one-minute batches. Use the
range query below if you need all 0.1 s samples within the same window.

The CSV endpoint paginates. Do **not** request the whole window with one large `$limit`:
the service caps a response, and a truncated request looks like a complete file. Order by
`:id` (the row's unique identifier), page with `$limit=50000` and `$offset=0, 50000, …`, and
stop when a page returns fewer rows. Then verify the total against `count(*)`:

```
$select=vehicle_id,frame_id,global_time,local_y,lane_id,v_vel,v_class
$where=location='i-80' AND global_time >= 1113433200000 AND global_time < 1113434100000
$order=:id
$limit=50000&$offset=<0, 50000, 100000, ...>
```

```
$select=count(*) AS n
$where=location='i-80' AND global_time >= 1113433200000 AND global_time < 1113434100000
```

Expected `n = 1226650`. Two traps: the CSV export quotes every field, and every response
repeats the header line — drop one header per response, not one per file. A first attempt
here that ignored both produced a file one row short per page, and an offset drift of the
same size, which `count(*)` caught. Ordering by `:id`, the row's unique identifier, is what
makes paging safe: sorting by `global_time` alone has ties, and a tie split across a page
boundary can duplicate one row and drop another.

The whole `i-80` location holds 4,566,387 rows (verified). Sibling sites in the same
dataset: `us-101` (Los Angeles) and the signalised arterials `lankershim` and `peachtree` —
the latter two are not conservation-law material.

## Reference checksums

These checksums are for the archived reference copies. Confirm the trajectory row count,
sampling step and panel cell count first when checking a new download.

| File | SHA-256 |
| --- | --- |
| `ngsim_i80_2005-04-13_1600-1615_raw_1s.csv` | `63c615dad21ad32ae9f5eed7626ed294733627f95e26b18b1050f77ccb4c8204` |
| `ngsim_i80_2005-04-13_1600-1615_panel_through.csv` | `98ee8df59462de275f0be02df96b02b36e7f76a3cc2cbcc8aca19df444b23f86` |
