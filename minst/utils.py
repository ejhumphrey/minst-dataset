import claudio
import colorama
import hashlib
from joblib import Parallel, delayed
import logging
import numpy as np
import os
import wave
import zipfile

COLOR_MAP = {
    "yellow": colorama.Fore.YELLOW,
    "red": colorama.Fore.RED,
    "green": colorama.Fore.GREEN,
    "blue": colorama.Fore.BLUE,
    "magenta": colorama.Fore.MAGENTA,
    "cyan": colorama.Fore.CYAN,
    "white": colorama.Fore.WHITE
}

logger = logging.getLogger(__name__)


def generate_id(prefix, name, hash_len=8):
    """Create a unique identifier for this entry.

    Parameters
    ----------
    prefix : str
        Prefix for the generated ID.

    name : str
        Filename, for deterministic hashing.

    hash_len : int, default=8
        Number of hashed characters to preserve.

    Returns
    -------
    uid : str
        Generated ID, as `prefix + md5(name)[:8]`
    """
    file_hash = hashlib.md5(name.encode('utf-8')).hexdigest()
    logger.debug("generate_id: prefix={}, name={}, fhash={}"
                 "".format(prefix, name, file_hash))
    return "{0}{1}".format(prefix, file_hash[:hash_len])


def filebase(fpath):
    """Return the file's basename without an extension, e.g. 'x/y.z' -> 'y'."""
    return os.path.splitext(os.path.basename(fpath))[0]


def note_distance(note_pair):
    """Get the distance in semitones between two named
    notes.

    E.g.
    (Bb1, B1) => 1
    (C4, B4) => 11
    (C5, Bb5) => 10

    Parameters
    ----------
    note_pair : tuple of ints

    Returns
    -------
    note_distance : int
    """
    char_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

    def apply_modifier(val, modifier):
        if modifier == "#":
            return val + 1
        elif modifier == 'b':
            return val - 1
        else:
            return val

    # get the chars
    first_note = [x for x in note_pair[0]]
    second_note = [x for x in note_pair[1]]

    first_name, first_oct = first_note[0], first_note[-1]
    first_mod = first_note[1] if len(first_note) == 3 else None
    second_name, second_oct = second_note[0], second_note[-1]
    second_mod = second_note[1] if len(second_note) == 3 else None

    base_dist = apply_modifier(char_map[second_name], second_mod) - \
        apply_modifier(char_map[first_name], first_mod)

    oct_diff = int(second_oct) - int(first_oct)
    base_dist += (oct_diff * 12)

    return base_dist


def create_directory(dname):
    """Create the output directory recursively if it doesn't already exist.

    Parameters
    ----------
    dname : str
        Directory to create.

    Returns
    -------
    success : bool
        True if the requested directory now exists.
    """
    if not os.path.exists(dname):
        os.makedirs(dname)
    return os.path.exists(dname)


def colorize(text, color="yellow"):
    """Colorize terminal text.

    Parameters
    ----------
    text : str
        Text to color.

    color : string
        Name of color to print

    Returns
    -------
    colored_text : str
        String of colored text.
    """

    return "{0}{1}{2}".format(COLOR_MAP[color], text,
                              colorama.Style.RESET_ALL)


def unzip_files(file_list, force=False):
    """Given a list of file paths, unzip them in place.

    Attempts to skip it if the extracted folder exists.

    Parameters
    ----------
    file_list : list of str
        Files to extract.

    force : bool, default=False
        Force the unzip if the file exists.

    Returns
    -------
    List of created outputs.
    """
    result_list = []
    for zip_path in file_list:
        working_dir = os.path.dirname(zip_path)
        zip_name = os.path.splitext(os.path.basename(zip_path))[0]
        new_folder_path = os.path.join(working_dir, zip_name)
        if force or not os.path.exists(new_folder_path):
            with zipfile.ZipFile(zip_path, 'r') as myzip:
                # Create a directory of the same name as the zip.
                os.makedirs(new_folder_path)
                myzip.extractall(path=new_folder_path)
                result_list.append(new_folder_path)

    return result_list


def check_audio_file(filename, min_duration=0.0):
    """Check the integrity of an audio file.

    Parameters
    ----------
    filename : str
        Path to an audio file on disk.

    min_duration : scalar, default=0.0
        Minimum time duration for the audio file to be considered valid.

    Returns
    -------
    status : bool
        True if legit, False otherwise.

    message : ExceptionType, or None
        None on success, else the exception class capturing the death.
    """
    status = False
    error = None
    try:
        aobj = claudio.fileio.AudioFile(filename, bytedepth=2)
        status = aobj.duration >= min_duration
    except (AssertionError, EOFError, wave.Error, ValueError) as derp:
        # This is a claudio bug, eventually will be a SoX error
        error = derp

    return status, error


def check_many_audio_files(fileset, min_duration=0.0, num_cpus=-1, verbose=0):
    """
    Tries to load every file, and returns a list of any file
    that fails to load.

    Parameters
    ----------
    fileset : list of str
        Set of audiofiles on disk.

    Returns
    -------
    status : list of (bool, ...)
        Aligned list of result tuples, given the input. The first item will
        contain the status (True if good), and the remainder will describe
        the issue caught.
    """
    pool = Parallel(n_jobs=num_cpus, verbose=0)
    fx = delayed(check_audio_file)
    return pool(fx(af, min_duration) for af in fileset)


def trim(filename, output_dir=None, duration=None):
    """Takes a single audio file, and standardizes it based
    on the parameters provided.

    Heads up! Modifies the file in place...

    Parameters
    ----------
    filename : str
        Full path to the audio file to work with.

    output_dir : str or None
        Path to write updated files to under the same basename. If None,
        overwrites the input file.

    duration : float or None
        If not None, trims the final audio file to final_duration
        seconds.

    Returns
    -------
    output_audio_path : str or None
        Valid full file path if succeeded, or None if failed.
    """
    output_fname = None
    if output_dir:
        create_directory(output_dir)
        output_fname = os.path.join(output_dir, os.path.basename(filename))

    # Note: output_fname of None will trim in place.
    success = claudio.sox.trim(filename, output_fname, 0, duration)
    if not success:
        logger.error(colorize("claudio.sox.trim Failed: {} -- "
                              "moving on...".format(filename), "red"))
        output_fname = None
    else:
        output_fname = filename if output_dir is None else output_fname

    return output_fname


def canny(nlen, beta, sig=2.0):
    """Create a canny filter.

    Parameters
    ----------
    nlen : int
        Length of the kernel.

    beta : scalar > 0
        Frequency of the sinusoid shape.

    sig : scalar > 0
        todo.

    Returns
    -------
    kernel : np.ndarray, ndim=1, len=nlen
        Kernel coefficients.
    """
    n = np.linspace(-beta, beta, nlen)
    alpha = (-n / np.power(sig, 2.))
    return alpha * np.exp(-(n ** 2.0) / (2.0 * (sig ** 2.0)))
