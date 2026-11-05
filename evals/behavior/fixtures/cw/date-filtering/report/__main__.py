import argparse
from datetime import date
from .filter import in_range

SAMPLE = [date(2024, 1, 1), date(2024, 1, 15), date(2024, 1, 31)]


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="start")
    p.add_argument("--to", dest="end")
    a = p.parse_args(argv)
    start = date.fromisoformat(a.start)
    end = date.fromisoformat(a.end)
    kept = [d for d in SAMPLE if in_range(d, start, end)]
    print("kept", len(kept), [d.isoformat() for d in kept])


if __name__ == "__main__":
    main()
