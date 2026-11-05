import argparse


def build_parser():
    p = argparse.ArgumentParser(prog="exporter")
    p.add_argument("--path", required=True)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    print(f"exporting {args.path}")


if __name__ == "__main__":
    main()
