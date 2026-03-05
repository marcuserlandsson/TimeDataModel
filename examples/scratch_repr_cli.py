#!/usr/bin/env python3
"""Print repr of TimeDataModel objects to the terminal (CLI view).

Run from project root:
  python examples/scratch_repr_cli.py
  # or with venv:
  .venv/bin/python examples/scratch_repr_cli.py
"""

from datetime import datetime, timedelta, timezone

from timedatamodel import (
    AggregationMethod,
    DataType,
    Frequency,
    HierarchicalTimeSeries,
    TimeSeriesList,
    set_repr_width,
)

# Optional: limit box width (e.g. 72 for narrow terminals); omit or set to None for no limit
# set_repr_width(72)


def hourly_ts(n=24, start="2024-01-15"):
    base = datetime.fromisoformat(f"{start}T00:00:00+00:00")
    return [base + timedelta(hours=i) for i in range(n)]


def main():
    ts = TimeSeriesList(
        Frequency.PT1H,
        timezone="UTC",
        timestamps=hourly_ts(24),
        values=[120 + 5 * (i % 7) for i in range(24)],
        name="power",
        unit="MW",
        data_type=DataType.OBSERVATION,
        description="Hourly power output from wind farm Alpha",
    )

    print("=== TimeSeriesList (terminal repr) ===")
    print(ts)
    print()

    # Coverage bar (gappy series)
    vals_gap = [float(i) for i in range(24)]
    for i in [5, 6, 7, 15, 16]:
        vals_gap[i] = None
    ts_gap = TimeSeriesList(
        Frequency.PT1H,
        timezone="UTC",
        timestamps=hourly_ts(24),
        values=vals_gap,
        name="gappy_signal",
        unit="kW",
    )
    print("=== CoverageBar (gappy series: missing at 5,6,7,15,16) ===")
    print(ts_gap.coverage_bar())
    print()

    # Hierarchy tree
    def make_ts(name):
        return TimeSeriesList(
            Frequency.PT1H,
            timezone="UTC",
            timestamps=hourly_ts(24),
            values=[100 + hash(name) % 100 for _ in range(24)],
            name=name,
            unit="MW",
            data_type=DataType.OBSERVATION,
        )

    tree_dict = {
        "total": {
            "Norway": {"Bergen": "bergen", "Oslo": "oslo", "Trondheim": "trondheim"},
            "Sweden": {"Stockholm": "stockholm", "Gothenburg": "gothenburg"},
        }
    }
    series_map = {
        "bergen": make_ts("Bergen"),
        "oslo": make_ts("Oslo"),
        "trondheim": make_ts("Trondheim"),
        "stockholm": make_ts("Stockholm"),
        "gothenburg": make_ts("Gothenburg"),
    }
    hts = HierarchicalTimeSeries.from_dict(
        tree_dict,
        series_map,
        levels=["region", "country", "city"],
        name="Nordic Wind Power",
        aggregation=AggregationMethod.SUM,
    )
    print("=== HierarchyTree (terminal repr) ===")
    print(hts.tree())
    print()

    # Uncomment to try width limiting:
    # print("With set_repr_width(50):")
    # set_repr_width(50)
    # print(ts)
    # set_repr_width(None)


if __name__ == "__main__":
    main()
