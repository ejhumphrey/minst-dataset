import glob
import logging
import os
import pandas as pd

import minst.utils as utils


logger = logging.getLogger(__name__)

NAME = 'philharmonia'
ONSET_DIR = os.path.join(os.path.dirname(__file__),
                         os.pardir, os.pardir,
                         "data", "onsets", NAME)


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


def collect(base_dir, articulations=["normal", "vibrato"],
            onset_dir=ONSET_DIR):
    """Convert a base directory of Philharmonia files to a pandas dataframe.

    Parameters
    ----------
    base_dir : str
        Full path to the base RWC directory.

    articulations : list of str
        Articulations over which to filter the data.

    onset_dir : str
        Path at which to look for onset data.

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
            onsets_file
    """
    logger.info("Scanning {} for files.".format(base_dir))

    root_dir = os.path.join(base_dir, "www.philharmonia.co.uk",
                            "assets/audio/samples")

    # These files download as {instrument}/{instrument}.zip.
    zip_fmt = os.path.join(root_dir, "*/*.zip")
    zip_files = glob.glob(zip_fmt)
    logger.debug("Found {} zipfiles at {}".format(len(zip_files), zip_fmt))
    utils.unzip_files(zip_files)

    articulation_skipped = []

    # Need this to be iterable.
    articulations = articulations if articulations else []

    indexes = []
    records = []
    # MP3s are extracted automatically as {instrument}/{instrument}/{fbase}.mp3
    audio_path_fmt = os.path.join(root_dir, "*/*/*.mp3")
    for audio_file_path in glob.glob(audio_path_fmt):
        (instrument, note, duration, dynamic,
            articulation) = parse(audio_file_path)

        art_conds = [not bool(articulations),
                     any([x in articulation for x in articulations])]
        if any(art_conds):
            uid = utils.generate_id(NAME, audio_file_path.split(base_dir)[-1])
            onsets = utils.find_onset_file_from_uid(uid, onset_dir)
            indexes.append(uid)
            records.append(
                dict(audio_file=audio_file_path,
                     dataset=NAME,
                     instrument=instrument,
                     note=note,
                     dynamic=dynamic,
                     onsets_file=onsets))
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
