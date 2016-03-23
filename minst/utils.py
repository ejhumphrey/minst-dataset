import hashlib
import os


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
