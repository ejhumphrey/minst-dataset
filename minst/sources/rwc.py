"""
# RWC
If obtained from AIST, the data will live on 12 CDs. Here, they have been
backed into a folder hierarchy like the following:

    {base_dir}/
        RWC_I_01/
            {num}/
                {num}{instrument}{style}{dynamic}.{fext}
        RWC_I_02
            ...
        RWC_I_12

Where...
 * base_dir : The path where the data are collated
 * num : A three-digit number contained in the folder
 * instrument : A two-character instrument code
 * style : A two-character style code
 * dynamic : A one-character loudness value

"""
import glob
import json
import logging
import os
import pandas as pd

import minst
import minst.utils as utils

logger = logging.getLogger(__name__)

RWC_INSTRUMENT_MAP_PATH = os.path.join(
    minst.DATA_DIR,
    "rwc_instrument_map.json")

RWC_INSTRUMENT_MAP = dict()
with open(RWC_INSTRUMENT_MAP_PATH, 'r') as fh:
    RWC_INSTRUMENT_MAP.update(**json.load(fh))


def instrument_code_to_name(rwc_instrument_code):
    """Use the rwc_instrument_map.json to convert an rwc_instrument_code
    to its instrument name.

    Parameters
    ----------
    rwc_instrument_code : str
        Two character instrument code

    Returns
    -------
    instrument_name : str
        Full instrument name, if it exists, else None
    """
    code = RWC_INSTRUMENT_MAP.get(rwc_instrument_code, None)
    return code if code else None


def parse(filename):
    """Takes an rwc path, and returns the extracted codes from the
    filename.

    Parameters
    ----------
    rwc_path : str
        Full path or basename. If full path, gets the basename.

    Returns
    -------
    instrument_name : str, or None if cannot be parsed.
    style_code : str
    dynamic_code : str
    """
    filebase = utils.filebase(filename)
    instrument_code = filebase[3:5]
    # Get the instrument name from the json file.
    instrument_name = instrument_code_to_name(instrument_code)
    style_code = filebase[5:7]
    dynamic_code = filebase[7]
    return instrument_name, style_code, dynamic_code


def collect(base_dir, dataset="rwc"):
    """Convert a base directory of RWC files to a pandas dataframe.

    Parameters
    ----------
    base_dir : str
        Full path to the base RWC directory.

    dataset : str
        Datset string to use in this df.

    Returns
    -------
    pandas.DataFrame
        Indexed by:
            id : [dataset identifier] + [8 char md5 of filename]
        With the following columns:
            audio_file : full path to original audio file.
            dataset : dataset it is from
            instrument : instrument label.
            dynamic : dynamic tag
    """
    logger.info("Scanning {} for audio files.".format(base_dir))

    indexes = []
    records = []
    for audio_file_path in glob.glob(os.path.join(base_dir, "*/*/*.flac")):
        instrument_name, style_code, dynamic_code = parse(audio_file_path)
        uid = utils.generate_id(dataset, utils.filebase(audio_file_path))
        indexes.append(uid)
        records.append(
            dict(audio_file=audio_file_path,
                 dataset=dataset,
                 instrument=instrument_name,
                 dynamic=dynamic_code))

    logger.info("Found {} files from RWC.".format(len(records)))

    return pd.DataFrame(records, index=indexes)
