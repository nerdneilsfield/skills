import argparse
from src.validate import validate
from src.write_json import write_json
from src.write_csv import write_csv
from src.summary import summarize


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("path")
    args = p.parse_args(argv)
    rows = validate(args.path)
    write_json(rows)
    write_csv(rows)
    summarize(rows)
