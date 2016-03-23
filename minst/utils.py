import hashlib
import os
import colorama
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
