import argparse
import logging
import os
import pandas as pd
import sys

import minst.logger

logger = logging.getLogger("collect_data")


def main(index_file, output_dir):
    df = pd.read_csv(index_file, index_col=0)
    dummy_onset = pd.DataFrame.from_records([dict(time=0.0)])
    onset_fmt = os.path.join(output_dir, "{}.csv")
    success = True
    for idx in df.index.tolist():
        fout = onset_fmt.format(idx)
        dummy_onset.to_csv(fout)
        success &= os.path.exists(fout)
    return success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "index_file",
        metavar="index_file", type=str,
        help="Filepath of the index to use.")
    parser.add_argument(
        "output_dir",
        metavar="output_dir", type=str,
        help="Output path for trivial onsets.")

    args = parser.parse_args()
    logging.config.dictConfig(minst.logger.get_config('INFO'))

    success = main(args.index_file, args.output_dir)
    sys.exit(0 if success else 1)
