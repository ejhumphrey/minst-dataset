"""Create an example notes dataset with N files sampled from
the original datasets.

Usage:
 example_datasets.py [options] <destination_dir> <source_index>...

Arguments:
 destination_dir  Directory to store the final note data.
 source_index     Indeces to use to generate the data.
                  These should be x_notes.csv files.

Options:
 --n_files=N      Number of files to sample from each source
                  dataset. [default: 4]
"""
from __future__ import print_function
import boltons.fileutils
from docopt import docopt
import logging
import logging.config
import os
import pandas as pd
import shutil
import sys
import time

import minst.logger
import minst.utils as utils

logger = logging.getLogger("example_datasets")


def copy_example_datasets(destination_dir, source_indeces, n_files):
    """Copy n_files from each instrument class in source_indexes
    to destination_dir, and create a new index file at the destination.

    Parameters
    ----------
    destination_dir : str

    source_indeces : list of str

    n_files : int
    """
    logger.info("copy_example_datasets({}, {}, n_files={})".format(
        destination_dir, source_indeces, n_files))

    boltons.fileutils.mkdir_p(destination_dir)

    indexes = []
    values = []
    for dataset in source_indeces:
        print(utils.colorize("Loading {}".format(dataset)))
        df = pd.read_csv(dataset, index_col=[0, 1])
        print("Available Notes:\n", df['instrument'].value_counts())

        # TODO: only use accepted instrument types
        for instrument_type in df['instrument'].unique():
            files = df[df['instrument'] == instrument_type].sample(n_files)
            for idx, row in files.iterrows():
                # TODO: copy the file to the destination, change the path.
                dest_filename = os.path.basename(row['note_file'])
                shutil.copy(row['note_file'], os.path.join(
                    destination_dir, dest_filename))

                indexes.append(idx)
                values.append(
                    [dataset, dest_filename, row['instrument']])
    result_df = pd.DataFrame(values,
                             columns=['dataset', 'note_file', 'instrument'],
                             index=indexes)
    result_df.to_csv(os.path.join(destination_dir, "notes_index.csv"))
    print("Copied {} files to {}".format(len(result_df), destination_dir))


if __name__ == "__main__":
    arguments = docopt(__doc__)
    print(arguments)

    level = 'INFO' if not arguments.get('--verbose') else 'DEBUG'
    logging.config.dictConfig(minst.logger.get_config(level))

    t0 = time.time()
    copy_example_datasets(
        arguments['<destination_dir>'],
        arguments['<source_index>'],
        int(arguments['--n_files']))
    t_end = time.time()
    print("example_datasets.py completed in: {}s".format(t_end - t0))
