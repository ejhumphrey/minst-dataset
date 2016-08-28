import glob
import logging
import os
import pandas as pd

import minst.utils as utils


logger = logging.getLogger(__name__)

NAME = 'good-sounds'
EXPECTED_ROOT_DIR = 'sound_files'
ONSET_DIR = os.path.join(os.path.dirname(__file__),
                         os.pardir, os.pardir,
                         "data", "onsets", NAME)


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
    if EXPECTED_ROOT_DIR in filename:
        filename = filename[filename.index(EXPECTED_ROOT_DIR) +
                            len(EXPECTED_ROOT_DIR):]
    (instrument, pack, take, note_id) = (
        filename.strip('/').split('/'))
    note_id = utils.filebase(note_id)
    return instrument, pack, take, note_id


def collect(base_dir, onset_dir=ONSET_DIR):
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
    zip_fmt = os.path.join(root_dir, "*/*.zip")
    zip_files = glob.glob(zip_fmt)
    logger.debug("Found {} zipfiles at {}".format(len(zip_files), zip_fmt))
    utils.unzip_files(zip_files)

    indexes = []
    records = []
    # Extracts as {base_dir}/sound_files/{instrument}/{pack}/{mic}/{fbase}.wav
    audio_fmt = os.path.join(root_dir, "*/*/*/*.wav")
    for audio_file_path in glob.glob(audio_fmt):
        (instrument, pack, take, note_id) = (
            parse(audio_file_path.split(root_dir)[1]))

        uid = utils.generate_id(NAME, audio_file_path.split(base_dir)[-1])
        onsets = utils.find_onset_file_from_uid(uid, onset_dir)
        indexes.append(uid)
        records.append(
            dict(audio_file=audio_file_path,
                 dataset=NAME,
                 instrument=instrument,
                 onsets_file=onsets))

    logger.info("Using {} files from {}.".format(len(records), NAME))
    return pd.DataFrame(records, index=indexes)
