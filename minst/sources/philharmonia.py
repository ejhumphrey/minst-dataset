import glob
import logging
import os
import pandas as pd

import minst.utils as utils


logger = logging.getLogger(__name__)

NAME = 'philharmonia'


def parse(filename):
    """Convert phil path to codes/parameters.

    Parameters
    ----------
    filename : full path.

    Returns
    -------
    parts : tuple, len=5
        From the filename, the following parts:
            (instrument, note, duration, dynamic, articulation).
    """
    audio_file_name = utils.filebase(filename)
    (instrument, note, duration, dynamic,
        articulation) = audio_file_name.split('_')
    return instrument, note, duration, dynamic, articulation


def collect(base_dir, articulations=["normal", "vibrato"]):
    """Convert a base directory of Philharmonia files to a pandas dataframe.

    Parameters
    ----------
    base_dir : str
        Full path to the base RWC directory.

    articulations : list of str
        Articulations over which to filter the data.

    Returns
    -------
    pandas.DataFrame
        With the following columns:
            id
            audio_file
            dataset
            instrument
            note
            dynamic
    """
    logger.info("Scanning {} for files.".format(base_dir))

    root_dir = os.path.join(base_dir, "www.philharmonia.co.uk",
                            "assets/audio/samples")

    # These files come in zips. Extract them as necessary.
    zip_files = glob.glob(os.path.join(root_dir, "*/*.zip"))
    utils.unzip_files(zip_files)

    articulation_skipped = []

    # Need this to be iterable.
    articulations = articulations if articulations else []

    indexes = []
    records = []
    for audio_file_path in glob.glob(os.path.join(root_dir, "*/*/*.mp3")):
        (instrument, note, duration, dynamic,
            articulation) = parse(audio_file_path)

        art_conds = [not bool(articulations),
                     any([x in articulation for x in articulations])]
        if any(art_conds):
            uid = utils.generate_id(NAME, audio_file_path)
            indexes.append(uid)
            records.append(
                dict(audio_file=audio_file_path,
                     dataset=NAME,
                     instrument=instrument,
                     note=note,
                     dynamic=dynamic))
        else:
            articulation_skipped += [audio_file_path]

    logger.info("Using {} files from {}.".format(len(records), NAME))
    logger.warn(
        utils.colorize("Skipped {} file(s) with articulation not in {}"
                       .format(len(articulation_skipped), articulations),
                       "red"))

    with open("log_philharmonia_skipped.txt", 'w') as fh:
        fh.write("\n".join(articulation_skipped))

    return pd.DataFrame(records, index=indexes)
