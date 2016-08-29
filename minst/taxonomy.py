import json
import os

import minst


CLASS_MAP_PATH = os.path.join(minst.DATA_DIR, "class_map.json")


class InstrumentClassMap(object):
    """Class for handling map between class names and the
    names they possibly could be from the datasets."""

    def __init__(self, file_path=CLASS_MAP_PATH):
        """
        Parameters
        ----------
        file_path : str
            Path to a JSON file of an instrument class map.
        """
        with open(file_path, 'r') as fh:
            self.data = json.load(fh)

        # Create the reverse map so we can efficiently do the
        # reverse lookup
        self.reverse_map = {}
        for classname in self.data:
            for item in self.data[classname]:
                self.reverse_map[item] = classname

        self.index_map = {}
        for i, classname in enumerate(sorted(self.data.keys())):
            self.index_map[classname] = i

    @property
    def allnames(self):
        """Return a complete list of all class names for searching the
        dataframe."""
        return sorted(self.reverse_map.keys())

    @property
    def classnames(self):
        return sorted(self.data.keys())

    def __getitem__(self, searchkey):
        """Get the actual class name. (Actually the reverse map)."""
        return self.reverse_map.get(searchkey, None)

    def get_index(self, searchkey):
        """Get the class index for training.

        This is actually the index of the sorted keys.

        Parameters
        ----------
        searchkey : str

        Returns
        -------
        index : int
        """
        return self.index_map[self[searchkey]]

    def from_index(self, index):
        """Get the instrument name for an index."""
        return sorted(self.data.keys())[index]

    @property
    def size(self):
        """Return the size of the index map (the number of
        data keys)
        """
        return len(self.data.keys())


def normalize_instrument_names(dframe):
    """Convert all the varied datasets representation of
    instrument names to the single one used in
    our class set.

    Parameters
    ----------
    dframe : pandas.DataFrame with an "instrument" column.

    Returns
    -------
    normalized_df : pandas.DataFrame
        A copy of the input dataframe, with instruments only from
        the InstrumentClassMap.
    """
    classmap = InstrumentClassMap()
    new_df = dframe.copy()
    new_df["instrument"] = [classmap[i] for i in dframe.instrument]
    return new_df
