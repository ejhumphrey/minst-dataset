import glob
import logging
import os
import pandas as pd

import minst.utils as utils


logger = logging.getLogger(__name__)

NAME = 'good-sounds'


def parse(filename):
    """Convert good-sounds path to codes/parameters.

    Parameters
    ----------
    filename : full path.

    Returns
    -------
    parts : tuple, len=5
        From the filename, the following parts:
            (instrument, pack, take, note_id)
    """
    (instrument, pack, take, note_id) = filename.strip('/').split('/')
    note_id = utils.filebase(filename)
    return instrument, pack, take, note_id


def collect(base_dir):
    """Convert a base directory of Good-Sounds files to a pandas dataframe.

    Parameters
    ----------
    base_dir : str
        Full path to the base Good-Sounds directory.

    Returns
    -------
    pandas.DataFrame
        With the following columns:
            id
            audio_file
            dataset
            instrument
    """
    logger.info("Scanning {} for files.".format(base_dir))

    root_dir = os.path.join(base_dir, "sound_files")

    # These files (might) come in zips.
    # TODO: Add unzipping in for this.
    # zip_files = glob.glob(os.path.join(root_dir, "*/*.zip"))
    # utils.unzip_files(zip_files)

    indexes = []
    records = []
    for audio_file_path in glob.glob(os.path.join(root_dir, "*/*/*/*.wav")):
        (instrument, pack, take, note_id) = (
            parse(audio_file_path.split(root_dir)[1]))

        uid = utils.generate_id(NAME, audio_file_path)
        indexes.append(uid)
        records.append(
            dict(audio_file=audio_file_path,
                 dataset=NAME,
                 instrument=instrument))

    logger.info("Using {} files from {}.".format(len(records), NAME))
    return pd.DataFrame(records, index=indexes)
