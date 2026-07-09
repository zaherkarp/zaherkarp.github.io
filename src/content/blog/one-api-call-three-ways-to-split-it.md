---
title: "One API call, three ways to split it: a FRED case study"
description: "Pull five FRED series once, cache the raw pull, then fan it out into per-year-per-indicator files three different ways — plus a fourth example: keeping the local store current with real-time incremental pulls instead of re-running the big fetch."
publishDate: 2026-07-09
draft: false
tags: ["python", "data-engineering", "apis", "sqlite"]
---

Every data pipeline eventually hits the same fork in the road: you've pulled a pile of records from somewhere expensive to query, and now you need to turn that pile into many small files, one per combination of dimensions. A reporting job that needs one file per region per month. A batch export that needs one file per customer per product. An economic dashboard that needs one file per year per indicator.

The pull itself is usually the easy part. It's what happens *after* the pull that tends to get messy, because there are a few genuinely different ways to fan one cache file out into many outputs, and each one trades a different resource for a different guarantee. This post walks through three of them, using the Federal Reserve's FRED API as a concrete example: we'll pull five economic indicators across their full history, cache the raw pull once, split it into per-year-per-indicator files three different ways, load the result into SQLite, add a fourth example for real-time API access so the local store stays current without re-running the big fetch, and finish with a small trend forecast.

## The problem shape

FRED (Federal Reserve Economic Data) publishes thousands of time series through a free public API. We'll use five well-known ones:

- `UNRATE` — unemployment rate
- `CPIAUCSL` — consumer price index
- `FEDFUNDS` — federal funds rate
- `PAYEMS` — nonfarm payrolls
- `DGS10` — 10-year treasury yield

Each series comes back as a list of `(date, value)` observations, monthly or daily depending on the series, going back decades. If we treat the *year* as the period dimension and the *series id* as the measure dimension, we land on exactly the same shape as the general problem: a big flat pull, and a need to split it into files keyed by `period|measure` — `2010_UNRATE.csv`, `2010_CPIAUCSL.csv`, `2011_UNRATE.csv`, and so on.

You'll need a free FRED API key (instant signup, no cost) to run this yourself: https://fred.stlouisfed.org/docs/api/api_key.html

## Step 0: pull once, cache to a flat file

This step is identical no matter which splitting approach you use afterward, so it's worth pulling out on its own. Hit the API once per series, write every observation to one local file, and don't try to be clever about organization yet. Just get everything onto disk in a shape you can reread cheaply.

```python
import requests
import csv
import os

FRED_API_KEY = os.environ["FRED_API_KEY"]
SERIES = ["UNRATE", "CPIAUCSL", "FEDFUNDS", "PAYEMS", "DGS10"]
CACHE_PATH = "raw_observations.dat"

def fetch_series(series_id):
    """One HTTP call per series, returns FRED's raw observation list."""
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()["observations"]

def build_cache():
    """Pull every series once, write every row to one flat cache file.

    Row format: year, series_id, date, value
    year doubles as our 'period' key, series_id as our 'measure' key.
    """
    with open(CACHE_PATH, "w", newline="") as out:
        writer = csv.writer(out)
        for series_id in SERIES:
            for obs in fetch_series(series_id):
                if obs["value"] == ".":
                    # FRED marks missing observations with a literal dot
                    continue
                year = obs["date"][:4]
                writer.writerow([year, series_id, obs["date"], obs["value"]])

if __name__ == "__main__":
    build_cache()
```

Five series, most going back 10-60 years, comes out to a modest cache file, maybe a few thousand rows. Small enough that any of the three approaches below will run in well under a second on this dataset — but the *pattern* is what matters, because the same three approaches behave very differently once you're pulling hundreds of series across decades of daily data instead of five series of mostly-monthly data.

Every row already carries its `year` (period) and `series_id` (measure), exactly like a warehouse export that includes its own partition keys. That's what makes the three splitting strategies below possible without a second trip to the API.

## Approach 1: single pass, many open writers

The simplest strategy: read the cache once, and for every row, look up (or create) a file handle keyed by `period|measure`. Keep every writer open until the whole file has been read, then close everything at once.

```python
import csv
import os

CACHE_PATH = "raw_observations.dat"
OUT_DIR = "by_period_measure"

def split_single_pass():
    os.makedirs(OUT_DIR, exist_ok=True)
    writers = {}  # "year_series" -> (file handle, csv.writer)
    with open(CACHE_PATH) as cache:
        for year, series_id, date, value in csv.reader(cache):
            key = f"{year}_{series_id}"
            if key not in writers:
                f = open(os.path.join(OUT_DIR, f"{key}.csv"), "w", newline="")
                w = csv.writer(f)
                w.writerow(["date", "value"])
                writers[key] = (f, w)
            writers[key][1].writerow([date, value])
    for f, _ in writers.values():
        f.close()

if __name__ == "__main__":
    split_single_pass()
```

With five series across, say, 60 years of history, that's at most a few hundred distinct `period|measure` keys, and therefore a few hundred file handles open at once. Comfortably under any operating system's default limit (typically 1024+ open files per process). One clean read of the cache, done.

The catch shows up at scale. If you were doing this against hundreds of FRED series across a century of daily data, you could be looking at tens of thousands of distinct keys, and the "keep every writer open" strategy runs into `OSError: Too many open files` well before you finish the loop.

## Approach 2: batched — discover first, write in waves

Approach 2 trades a single read of the cache for several reads, in exchange for a hard ceiling on how many file handles are ever open at once.

The first pass touches the cache but doesn't write anything — it just figures out which `period|measure` keys exist and how big each one is. That gives you a plan before you commit any disk I/O.

```python
import csv
import os

CACHE_PATH = "raw_observations.dat"
OUT_DIR = "by_period_measure"
BATCH_SIZE = 25

def discover_keys():
    """First pass: find every distinct key and its row count, write nothing."""
    counts = {}
    with open(CACHE_PATH) as cache:
        for year, series_id, _, _ in csv.reader(cache):
            key = f"{year}_{series_id}"
            counts[key] = counts.get(key, 0) + 1
    return counts

def split_batched():
    os.makedirs(OUT_DIR, exist_ok=True)
    counts = discover_keys()
    keys = sorted(counts)
    n_batches = -(-len(keys) // BATCH_SIZE)  # ceiling division
    print(f"{len(keys)} period-measure combos, {BATCH_SIZE} per batch, "
          f"{n_batches} batches")
    for batch_num, start in enumerate(range(0, len(keys), BATCH_SIZE), 1):
        batch_keys = set(keys[start:start + BATCH_SIZE])
        writers = {}
        for key in batch_keys:
            f = open(os.path.join(OUT_DIR, f"{key}.csv"), "w", newline="")
            w = csv.writer(f)
            w.writerow(["date", "value"])
            writers[key] = (f, w)
        # reread the cache, keep only the rows that belong to this batch
        with open(CACHE_PATH) as cache:
            for year, series_id, date, value in csv.reader(cache):
                key = f"{year}_{series_id}"
                if key in batch_keys:
                    writers[key][1].writerow([date, value])
        for f, _ in writers.values():
            f.close()
        print(f"batch {batch_num}/{n_batches} done")

if __name__ == "__main__":
    split_batched()
```

Now no more than `BATCH_SIZE` files are ever open simultaneously, and the discovery pass gives you a plan you can print, log, or use to size the batches before committing to anything. It's also naturally resumable — a "batch N done" marker after each wave, and a crash partway through only costs you the current batch, not the whole job. The price is that the cache gets reread once per batch: with our five-series example that's a handful of rereads of a small file, trivial; at hundreds of series and a large batch count, that's hundreds of full passes over a potentially large cache.

## Approach 3: index and seek

The third strategy tries to get both a single read of the cache *and* a bounded number of open handles, by paying for it with an index and random-access reads.

The first pass builds a map from `period|measure` to the exact byte offsets where that key's rows live in the cache file. The second pass never scans linearly at all — it seeks directly to each recorded offset and reads just that line.

```python
import csv
import os

CACHE_PATH = "raw_observations.dat"
OUT_DIR = "by_period_measure"

def build_offset_index():
    """First pass: record the byte offset of every row, grouped by key."""
    index = {}
    with open(CACHE_PATH, "rb") as cache:
        offset = cache.tell()
        line = cache.readline()
        while line:
            year, series_id, _, _ = line.decode().strip().split(",")
            key = f"{year}_{series_id}"
            index.setdefault(key, []).append(offset)
            offset = cache.tell()
            line = cache.readline()
    return index

def split_indexed():
    os.makedirs(OUT_DIR, exist_ok=True)
    index = build_offset_index()
    with open(CACHE_PATH, "rb") as cache:
        for key, offsets in index.items():
            out_path = os.path.join(OUT_DIR, f"{key}.csv")
            with open(out_path, "w", newline="") as out:
                writer = csv.writer(out)
                writer.writerow(["date", "value"])
                for off in offsets:
                    cache.seek(off)
                    year, series_id, date, value = (
                        cache.readline().decode().strip().split(",")
                    )
                    writer.writerow([date, value])

if __name__ == "__main__":
    split_indexed()
```

Only one output file is ever open at a time, and the cache itself is read exactly once in terms of total bytes touched — but "read once" is doing some hand-waving here, because the reads are scattered across the file in whatever order the rows for a given key happen to appear. If a series' rows are clustered together in the cache (say, because the cache was written series-by-series, as ours is), the seeks are cheap. If they were interleaved — imagine pulling all series for 2020, then all series for 2021, then... — the seeks jump all over the file and disk I/O dominates. This approach only pays off when the data is already sorted or naturally clustered by the key you're splitting on; forcing that clustering usually means sorting the cache first, which just moves the cost rather than removing it.

## The trade-off, side by side

| | Cache reads | Open handles | Resumable | Best when |
|---|---|---|---|---|
| **1. Single pass** | 1 | up to N (all keys) | No | Key count is small enough to fit under the OS file-handle limit |
| **2. Batched** | 1 per batch | bounded by batch size | Yes | Key count is large, or you want progress checkpoints |
| **3. Indexed seek** | 1 (scattered) | 1 | No | Data is already clustered/sorted by the split key |

For five FRED series over a few decades — a few hundred keys at most — approach 1 is more than sufficient and is the simplest code to read, debug, and maintain. The other two only start earning their complexity once the key count climbs into the thousands or the cache itself becomes too large to reread cheaply.

## Loading the split into SQLite

Flat files are a fine intermediate format, but once you want to actually query across periods and measures, SQLite earns its keep. Rather than reading all those small files back in, we load directly from the original cache — the split files above exist to demonstrate the three strategies, but SQLite's own indexing does the same job of "get me the rows for this key" without the file-per-key overhead at all.

```python
import csv
import sqlite3

CACHE_PATH = "raw_observations.dat"
DB_PATH = "fred.db"

def load_into_sqlite():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS observations (
            period  TEXT,
            measure TEXT,
            date    TEXT,
            value   REAL
        )
    """)
    conn.execute("DELETE FROM observations")  # keep this idempotent for reruns
    with open(CACHE_PATH) as cache:
        rows = [
            (year, series_id, date, float(value))
            for year, series_id, date, value in csv.reader(cache)
        ]
    conn.executemany(
        "INSERT INTO observations (period, measure, date, value) VALUES (?, ?, ?, ?)",
        rows,
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_measure_period "
        "ON observations (measure, period)"
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    load_into_sqlite()
```

One table, one index on `(measure, period)`, and every one of those `period|measure` slices from before is now just a `WHERE measure = ? AND period = ?` away, no file lookups needed.

## The fourth example: real-time access without a re-pull

Everything so far treats the pull as a one-time event: history lands once, and all the interesting work happens offline. But FRED keeps publishing — `DGS10` gets a new observation every trading day, `UNRATE` every month. The moment this pipeline is more than a demo, a new question appears alongside the splitting one: how do you keep the local store current without re-paying for the entire pull? Re-running Step 0 downloads decades of history to pick up a handful of new rows, which is exactly the kind of expensive round trip the cache existed to avoid.

The answer is to make the API do the filtering. The observations endpoint accepts an `observation_start` parameter, so the refresh becomes a two-step conversation: ask SQLite for the newest date it already holds per series, then ask the API only for observations after that date.

```python
import datetime
import os
import sqlite3
import requests

FRED_API_KEY = os.environ["FRED_API_KEY"]
SERIES = ["UNRATE", "CPIAUCSL", "FEDFUNDS", "PAYEMS", "DGS10"]
DB_PATH = "fred.db"

def fetch_since(series_id, start_date):
    """One HTTP call, returns only observations on or after start_date."""
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start_date,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()["observations"]

def refresh_latest():
    conn = sqlite3.connect(DB_PATH)
    for series_id in SERIES:
        (last_date,) = conn.execute(
            "SELECT MAX(date) FROM observations WHERE measure = ?",
            (series_id,),
        ).fetchone()
        next_day = (
            datetime.date.fromisoformat(last_date) + datetime.timedelta(days=1)
        ).isoformat()
        new_rows = [
            (obs["date"][:4], series_id, obs["date"], float(obs["value"]))
            for obs in fetch_since(series_id, next_day)
            if obs["value"] != "."
        ]
        conn.executemany(
            "INSERT INTO observations (period, measure, date, value) "
            "VALUES (?, ?, ?, ?)",
            new_rows,
        )
        print(f"{series_id}: {len(new_rows)} new observations")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    refresh_latest()
```

Each run makes one bounded API call per series and appends only what's new — most days that's zero or one row per series, a response measured in bytes rather than decades. Because the request window always starts strictly after the local maximum date, rerunning it is harmless: a second run finds nothing new and inserts nothing. Put it on a scheduler at whatever cadence "real time" means for your data (hourly is plenty for economic series that update daily at most) and the store stays current for the cost of five tiny requests.

One honest caveat: incremental append catches new observations, not revisions. FRED revises history — payroll numbers get restated, index series get re-benchmarked — and the API exposes those vintages through its `realtime_start` / `realtime_end` parameters. An append-only refresh never sees a revision to a date it already holds. The pragmatic pattern is to run both loops: the incremental refresh on a tight schedule for freshness, and the full Step 0 re-pull on a slow one (weekly or monthly) to reconcile whatever history moved underneath you.

And if what you actually need is the single freshest value at request time — a dashboard tile showing today's 10-year yield — skip the pipeline entirely for that one read: `sort_order=desc&limit=1` on the same endpoint returns just the latest observation in one tiny response. Wrap it in a short TTL cache (even sixty seconds) so a page full of tiles doesn't turn into a request storm, and let the SQLite store keep serving everything historical.

## The finale: a small trend forecast

With the data sitting in SQLite, the last step is to do something with it. We'll keep it simple and honest: a naive linear trend per series, fit on yearly averages, projected one year forward. This isn't a serious forecasting method — real economic series have seasonality, structural breaks, and plenty of nonlinearity — but it's a clean demonstration of going from raw pull to a derived insight entirely offline, no further API calls required.

```python
import sqlite3
import numpy as np

DB_PATH = "fred.db"

def forecast_next_period():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("""
        SELECT measure, period, AVG(value)
        FROM observations
        GROUP BY measure, period
        ORDER BY measure, period
    """)
    by_measure = {}
    for measure, period, avg_value in cur.fetchall():
        by_measure.setdefault(measure, []).append((int(period), avg_value))
    conn.close()
    results = {}
    for measure, points in by_measure.items():
        years = np.array([p[0] for p in points])
        values = np.array([p[1] for p in points])
        slope, intercept = np.polyfit(years, values, 1)
        next_year = int(years.max()) + 1
        forecast = slope * next_year + intercept
        results[measure] = (next_year, round(float(forecast), 3))
    return results

if __name__ == "__main__":
    for measure, (year, value) in forecast_next_period().items():
        print(f"{measure}: projected {year} average = {value}")
```

Running that prints one naive projection per series, entirely from data that's already sitting on local disk. No further network calls, no reprocessing of the original cache — everything downstream of the SQLite load runs against an indexed local table.

## Visualizing the forecast, three ways

A number in a terminal is fine for a script, but if this forecast is going in front of anyone who isn't going to read the SQL, the visualization matters as much as the math. Three styles that consistently work for non-technical audiences:

- **Trend line with a shaded projection band** — shows the shape of the history and signals "this next bit is an estimate" without saying so in words.
- **Big-number KPI card** — the projected value front and center with a small sparkline for context. Fastest to read, best as a supporting tile next to a fuller chart.
- **Annotated trend line** — the trend plus a plain-English sentence pointing at the projected point. Usually the safest default, since it doesn't ask the reader to interpret anything on their own.

All three pull from the same `by_measure` data the forecast step already computed, so there's no new querying involved, just presentation.

```python
import sqlite3
import matplotlib.pyplot as plt

DB_PATH = "fred.db"
COLORS = {
    "UNRATE": "#185FA5",
    "CPIAUCSL": "#0F6E56",
    "FEDFUNDS": "#993C1D",
    "PAYEMS": "#534AB7",
    "DGS10": "#72243E",
}

def load_yearly_averages():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("""
        SELECT measure, period, AVG(value)
        FROM observations
        GROUP BY measure, period
        ORDER BY measure, period
    """)
    by_measure = {}
    for measure, period, avg_value in cur.fetchall():
        by_measure.setdefault(measure, []).append((int(period), avg_value))
    conn.close()
    return by_measure

def plot_trend_band(measure, points, next_year, forecast, out_path):
    years = [p[0] for p in points]
    values = [p[1] for p in points]
    color = COLORS.get(measure, "#444441")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(years, values, color=color, linewidth=2)
    ax.plot([years[-1], next_year], [values[-1], forecast],
            color=color, linewidth=2, linestyle="--")
    ax.fill_between(
        [years[-1], next_year],
        [values[-1] - 0.4, forecast - 0.6],
        [values[-1] + 0.4, forecast + 0.6],
        color=color, alpha=0.15,
    )
    ax.scatter([next_year], [forecast], color=color, s=40, zorder=5)
    ax.set_title(f"{measure}: history + {next_year} projection", loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

def plot_kpi_card(measure, points, next_year, forecast, out_path):
    years = [p[0] for p in points]
    values = [p[1] for p in points]
    color = COLORS.get(measure, "#444441")
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.axis("off")
    axins = ax.inset_axes([0.06, 0.06, 0.88, 0.32])
    axins.plot(years, values, color="#B4B2A9", linewidth=1.5)
    axins.axis("off")
    ax.text(0.06, 0.88, measure, fontsize=13, transform=ax.transAxes)
    ax.text(0.06, 0.5, f"{forecast:.2f}", fontsize=40, fontweight="bold",
            color=color, transform=ax.transAxes)
    ax.text(0.58, 0.58, f"projected {next_year}", fontsize=12,
            color="#993C1D", transform=ax.transAxes)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

def plot_annotated_line(measure, points, next_year, forecast, out_path):
    years = [p[0] for p in points]
    values = [p[1] for p in points]
    color = COLORS.get(measure, "#444441")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(years, values, color=color, linewidth=2)
    ax.scatter([next_year], [forecast], color="#D85A30", s=55, zorder=5)
    ax.annotate(
        f"Expected to reach about {forecast:.2f} by {next_year}",
        xy=(next_year, forecast), xytext=(years[len(years) // 4], max(values) + 0.6),
        fontsize=11, arrowprops=dict(arrowstyle="->", color="#5F5E5A", lw=1.2),
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(f"{measure}: {next_year} outlook", loc="left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

def build_all_visuals():
    by_measure = load_yearly_averages()
    forecasts = forecast_next_period()  # from the forecasting step above
    for measure, points in by_measure.items():
        next_year, forecast = forecasts[measure]
        plot_trend_band(measure, points, next_year, forecast, f"{measure}_trend.png")
        plot_kpi_card(measure, points, next_year, forecast, f"{measure}_kpi.png")
        plot_annotated_line(measure, points, next_year, forecast, f"{measure}_annotated.png")

if __name__ == "__main__":
    build_all_visuals()
```

Run that after the forecast step and you get three PNGs per series, no extra queries and no extra API calls. In practice, the annotated line works well as the main chart, with a KPI card pulled out as a supporting tile for whichever series matters most to the audience in the room.

## The shape of the lesson

Zoom out and the whole pipeline is really just three decisions, made once each:

1. **How do I get the data locally with the fewest expensive round trips?** One pull per series, cached to flat file, is as cheap as it gets.
2. **How do I reorganize that cache into the shape my next step needs?** This is where approaches 1, 2, and 3 come in, and the right one depends entirely on how many keys you're splitting into and how large the cache is — not on which one feels most sophisticated. For five FRED series, approach 1 wins on simplicity with room to spare. For a warehouse export with hundreds of measures across a hundred periods, approach 2's bounded handles and resumability usually win. Approach 3 is worth reaching for only when the data's natural order already matches the split you need.
3. **How do I keep the local copy fresh without re-paying for the pull?** The incremental refresh answers this with one bounded call per series, the full re-pull demotes to a slow-cadence reconciliation job for revisions, and the serve-time `limit=1` fetch covers the one read that genuinely can't wait.

Everything after that, the SQLite load and the trend forecast, is just normal local processing on data you no longer need to fetch in bulk again.
