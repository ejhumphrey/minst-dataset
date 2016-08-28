import glob
import logging
import os
import pandas as pd
import re

import minst.utils as utils

logger = logging.getLogger(__name__)

NAME = 'uiowa'
ONSET_DIR = os.path.join(os.path.dirname(__file__),
                         os.pardir, os.pardir,
                         "data", "onsets", NAME)


def parse(filename):
    """Decode a filename matching the UIowa format.

    Parameters
    ----------
    filename : str
        A filename conforming to the UIowa MIS conventions.

    Returns
    -------
    instrument : str, or None
        Instrument name

    dynamic : str
        Dymanic marker

    notevalue : str
        Note names for the file.
    """
    filename = utils.filebase(filename)
    parameters = [x.strip() for x in filename.split('.')]
    instrument = parameters.pop(0)
    # This regex matches note names with a preceeding and following '.'
    note_match = re.search(r"(?<=\.)[A-Fb#0-6]*(?<!\.)", filename)
    notevalue = filename[note_match.start():note_match.end()] \
        if note_match else None
    # This regex matches dynamic chars with a preceeding and following '.'
    dynamic_match = re.search(r"(?<=\.)[f|p|m]*(?<!\.)", filename)
    dynamic = filename[dynamic_match.start():dynamic_match.end()] \
        if dynamic_match else None
    return instrument, dynamic, notevalue


def num_notes_from_filename(filename):
    """Return the expected number of notes in a UIowa filename if it can be
    determined.

    E.g.
    Bb1B1 => 2
    C4B4 => 12
    C5Bb5 => 10
    B3 => 1
    booger => None

    Parameters
    ----------
    filename : str
        A filename potentially conforming to the UIowa MIS conventions.

    Returns
    -------
    num_notes : int, or None
        Number of notes expected to be in the file, or None if this
        information cannot be confidently inferred.
    """
    instrument, dynamic, notevalue = parse(filename)
    result = None

    if notevalue:
        notes = re.findall(r"([A-F][b#]?[0-6])", notevalue)
        if len(notes) == 1:
            result = 1
        elif len(notes) == 2:
            # Get note distance
            result = 1 + utils.note_distance(notes)

    return result


def collect(base_dir, depth=6, fext="*.aif*", onset_dir=ONSET_DIR):
    """Convert a base directory of UIowa files to a pandas dataframe.

    Parameters
    ----------
    base_dir : str
        Full path to the base RWC directory.

    Returns
    -------
    pandas.DataFrame
        With the following columns:
            id
            audio_file
            dataset
            instrument
            dynamic
            note
    """
    logger.info("Scanning {} for audio files.".format(base_dir))

    indexes = []
    records = []
    root_dir = os.path.join(base_dir, "theremin.music.uiowa.edu",
                            "sound files", "MIS")
    for n in range(depth):
        glbpath = os.path.join(root_dir, "/".join(["*"] * n), fext)
        for audio_file_path in glob.glob(glbpath):
            instrument, dynamic, notevalue = parse(audio_file_path)
            uid = utils.generate_id(NAME, audio_file_path.split(base_dir)[-1])
            onsets = utils.find_onset_file_from_uid(uid, onset_dir)
            indexes.append(uid)
            records.append(
                dict(audio_file=audio_file_path,
                     dataset=NAME,
                     instrument=instrument,
                     dynamic=dynamic,
                     note=notevalue,
                     onsets_file=onsets))

    logger.info("Found {} files from {}.".format(len(records), NAME))

    return pd.DataFrame(records, index=indexes)
