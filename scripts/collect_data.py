import argparse
import os
import sys

import minst.sources


def build_index(dataset, base_directory, output_file):
    df = minst.sources.SOURCES[dataset].collect(base_directory)
    df.to_csv(output_file)
    return os.path.exists(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "dataset",
        metavar="dataset", type=str,
        help="Name of the dataset to collect.")
    parser.add_argument(
        "base_dir",
        metavar="base_dir", type=str,
        help="Output path for cut-point estimations.")
    parser.add_argument(
        "index_file",
        metavar="index_file", type=str,
        help="A dframe in CSV format.")

    args = parser.parse_args()
    success = build_index(args.dataset, args.base_dir, args.index_file)
    sys.exit(0 if success else 1)
