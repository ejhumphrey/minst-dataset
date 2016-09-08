import argparse
import logging
import logging.config
import os
import sys

import minst.logger
import minst.sources
import minst.taxonomy
import minst.utils as utils

logger = logging.getLogger("collect_data")


def build_index(dataset, base_directory, output_file, backup_index=None,
                strict_taxonomy=False):
    df = minst.sources.SOURCES[dataset].collect(base_directory)
    if not df.empty:
        if strict_taxonomy:
            df_norm = minst.taxonomy.normalize_instrument_names(df)
            df = df.loc[df_norm.instrument.dropna().index]
    else:
        logger.warning(utils.colorize("Collecting {} failed; is the data "
                                      "vailable at {}?"
                                      .format(dataset, base_directory)))

    df.to_csv(output_file)
    if backup_index is not None:
        df.audio_file.to_csv(backup_index)
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
    parser.add_argument(
        "--backup_index", default=None,
        metavar="backup_index", type=str,
        help="A backup mapping between file indexes and source audio names.")
    parser.add_argument(
        "--strict_taxonomy", action="store_true",
        help="If True, filter rows based on the target taxonomy.")

    args = parser.parse_args()
    logging.config.dictConfig(minst.logger.get_config('INFO'))

    success = build_index(args.dataset, args.base_dir,
                          args.index_file, args.backup_index,
                          args.strict_taxonomy)
    sys.exit(0 if success else 1)

