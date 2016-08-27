"""Perform various functions dealing with datasets.

Usage:
 manage_dataset.py join <sources>... --output=MASTER_INDEX
 manage_dataset.py split <source_index> <test_set> <train_val_split> <output>
 manage_dataset.py example [options] <destination_dir> <source_index>... --n_files=N

Arguments:
 join     Combine index csv files into one file.
 split    Perform a train-test split.
 example  Create an example notes dataset with N files sampled from
          the original datasets.

Options:
"""
from __future__ import print_function
import boltons.fileutils
from docopt import docopt
import logging
import logging.config
import os
import pandas as pd
import shutil
import time

import minst.logger
import minst.model
import minst.taxonomy
import minst.utils as utils

logger = logging.getLogger('manage_dataset')


def join_note_files(sources, output_path):
    """Load all of the sources into memory, join them to one dataframe,
    and write them back out to output_path.
    """
    source_data = []
    for path in sources:
        source_data.append(pd.read_csv(path, index_col=0))

    final_data = pd.concat(source_data)
    boltons.fileutils.mkdir_p(os.path.dirname(output_path))
    final_data.to_csv(output_path)


def train_test_split(source_index, test_set, train_val_split, output):
    """Using test_set as the 'hold-out-set', segment source_index
    into train/test splits at the ratio train_test_split, and
    write the result to output.
    """
    source = pd.read_csv(source_index, index_col=0)
    collection = minst.model.Collection.from_dataframe(source)

    partition_index_df = minst.model.partition_collection(
        collection, test_set, train_val_split)

    partition_index_df.to_csv(output)


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
                    [row['dataset'], dest_filename, row['instrument']])
    result_df = pd.DataFrame(values,
                             columns=['dataset', 'note_file', 'instrument'],
                             index=indexes)
    result_df = minst.taxonomy.normalize_instrument_names(result_df)
    result_df.to_csv(os.path.join(destination_dir, "notes_index.csv"))
    print("Copied {} files to {}".format(len(result_df), destination_dir))


if __name__ == "__main__":
    arguments = docopt(__doc__)
    print(arguments)

    level = 'INFO' if not arguments.get('--verbose') else 'DEBUG'
    logging.config.dictConfig(minst.logger.get_config(level))

    t0 = time.time()
    if arguments['join']:
        join_note_files(arguments['<sources>'], arguments['--output'])
    elif arguments['split']:
        train_test_split(arguments['<source_index>'][0],
                         # the above requires the [0] because we use
                         # source_index as a list for examples...
                         arguments['<test_set>'],
                         float(arguments['<train_val_split>']),
                         arguments['<output>'])
    elif arguments['example']:
        copy_example_datasets(
            arguments['<destination_dir>'],
            arguments['<source_index>'],
            int(arguments['--n_files']))
    t_end = time.time()
    print("manage_dataset.py completed in: {}s".format(t_end - t0))
