"""Perform various functions dealing with datasets.

Usage:
 manage_dataset.py join <sources>... --output=MASTER_INDEX
 manage_dataset.py split <source_index> <test_set> <train_val_split> <output>
 manage_dataset.py example [options] <destination_dir> \
    <source_index>... \
    <note_audio_dir> \
    --n_per_instrument=N \


Arguments:
 join     Combine index csv files into one file.
 split    Perform a train-test split.
 example  Create an example notes dataset with N files sampled from
          the original datasets.

Options:
"""
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


def join_dataframes(sources):
    source_data = []
    for path in sources:
        source_data.append(pd.read_csv(path, index_col=0))

    return pd.concat(source_data)


def join_note_files(sources, output_index):
    """Load all of the sources into memory, join them to one dataframe,
    and write them back out to output_index.
    """
    final_data = join_dataframes(sources)
    final_data.to_csv(output_index)
    return os.path.exists(output_index)


def train_test_split(source_index, test_set, train_val_split, output_index):
    """Using test_set as the 'hold-out-set', segment source_index
    into train/test splits at the ratio train_test_split, and
    write the result to output.
    """
    source = pd.read_csv(source_index, index_col=0)
    collection = minst.model.Collection.from_dataframe(source)

    partition_index_df = minst.model.partition_collection(
        collection, test_set, train_val_split)

    partition_index_df.to_csv(output_index)
    return os.path.exists(output_index)


def create_example_dataset(destination_dir, source_indexes, note_audio_dir,
                           n_per_instrument, output_index="master_index.csv",
                           partition_index_fmt="{}_test_partition.csv",
                           train_val_split=0.2):
    """Copy `n_per_instrument` from each instrument class in source_indexes
    to destination_dir, and create a new index file at the destination.

    Parameters
    ----------
    destination_dir : str
        Output path for writing data.

    source_indexes : list of str
        Set of index paths to use.

    n_per_instrument : int
        Number of observations to sample per instrument.

    output_index : str
        Basename of the output index to write.

    Returns
    -------
    success : bool
        True if the process completed successfully.
    """
    logger.info("create_example_dataset({}, {}, n_per_instrument={})".format(
        destination_dir, source_indexes, n_per_instrument))

    boltons.fileutils.mkdir_p(destination_dir)

    dframe = join_dataframes(source_indexes)
    dframe = minst.taxonomy.normalize_instrument_names(dframe)

    indexes = []
    values = []
    for dataset in dframe.dataset.unique():
        dset_df = dframe[dframe.dataset == dataset]
        logger.info("Dataset: {} Available Notes:\n {}"
                    .format(dataset, dset_df['instrument'].value_counts()))

        # TODO: only use accepted instrument types
        for instrument_type in dset_df.instrument.unique():
            inst_df = dset_df[dset_df.instrument == instrument_type]
            records = inst_df.sample(n_per_instrument)
            for idx, row in records.iterrows():

                shutil.copy(os.path.join(note_audio_dir, row['audio_file']),
                            os.path.join(destination_dir, row['audio_file']))
                indexes.append(idx)
                values.append(row)

    result_df = pd.DataFrame(values, index=indexes)
    output_file = os.path.join(destination_dir, output_index)
    result_df.to_csv(output_file)
    logger.info("Copied {} files to {}"
                .format(len(result_df), destination_dir))

    success = True
    if len(result_df.dataset.unique()) < 2:
        raise ValueError("Need more datasets for partitioning!")

    for test_set in result_df.dataset.unique():
        partition_index = os.path.join(destination_dir,
                                       partition_index_fmt.format(test_set))
        success &= train_test_split(output_file, test_set, train_val_split,
                                    partition_index)
    return os.path.exists(output_file) and success


if __name__ == "__main__":
    arguments = docopt(__doc__)
    logger.debug(arguments)

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
        create_example_dataset(
            arguments['<destination_dir>'],
            arguments['<source_index>'],
            arguments['<note_audio_dir>'],
            int(arguments['--n_per_instrument']))
    t_end = time.time()
    logger.info("manage_dataset.py completed in: {}s".format(t_end - t0))
