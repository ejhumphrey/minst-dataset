import copy
import json
import jsonschema
import logging
import pandas as pd
import os
from sklearn.cross_validation import train_test_split

import minst.utils as utils

logger = logging.getLogger(__name__)


class MissingDataException(Exception):
    pass


class Observation(object):
    """Document model each item in the collection."""

    # This should use package resources :o(
    SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema',
                               'observation.json')
    SCHEMA = json.load(open(SCHEMA_PATH))

    def __init__(self, index, dataset, audio_file, instrument, source_index,
                 start_time, duration, note_number=None, dynamic='',
                 partition=''):
        """Model definition for an instrument observation.

        Parameters
        ----------
        index :

        dataset :

        audio_file : str
            Relative file path to an audiofile.

        instrument :

        source_index :

        start_time :

        duration :

        note_number :

        dynamic :

        partition :

        Returns
        -------
        obs : Observation
            Populated observation
        """
        self.index = index
        self.dataset = dataset
        self.audio_file = audio_file
        self.instrument = instrument
        self.source_index = source_index
        self.start_time = start_time
        self.duration = duration
        self.note_number = note_number
        self.dynamic = dynamic
        self.partition = partition

    def to_builtin(self):
        return self.__dict__.copy()

    @classmethod
    def from_series(cls, series):
        """Convert a pd.Series to an Observation."""
        return cls(index=series.name, **series.to_dict())

    def to_series(self):
        """Convert to a flat series (ie make features a column)

        Returns
        -------
        pandas.Series
        """
        flat_dict = self.to_dict()
        name = flat_dict.pop("index")
        return pd.Series(data=flat_dict, name=name)

    def to_dict(self):
        return self.__dict__.copy()

    def __getitem__(self, key):
        return self.__dict__[key]

    def validate(self, schema=None, verbose=False, check_files=True):
        """Returns True if valid.
        """
        schema = self.SCHEMA if schema is None else schema
        success = True
        try:
            jsonschema.validate(self.to_builtin(), schema)
        except jsonschema.ValidationError as derp:
            success = False
            if verbose:
                print("Failed schema test: \n{}".format(derp))
        if success and check_files:
            success &= utils.check_audio_file(self.audio_file)[0]
            if not success and verbose:
                print("Failed file check: \n{}".format(self.audio_file))

        return success


def _enforce_obs(obs, audio_root='', strict=True):
    """Get dict from an Observation if an observation, else just dict"""
    audio_file = obs['audio_file']
    escaped_audio_file = os.path.join(audio_root, audio_file)
    file_checks = [os.path.exists(audio_file),
                   os.path.exists(escaped_audio_file)]
    if not any(file_checks) and strict:
        raise MissingDataException(
            "Audio file(s) missing:\n\tbase: {}\n\tescaped:{}"
            "".format(audio_file, escaped_audio_file))

    if isinstance(obs, Observation):
        obs = obs.to_dict()
    obs['audio_file'] = escaped_audio_file if file_checks[1] else audio_file
    return obs


class Collection(object):
    """Dictionary-like collection of Observations (maintains order).

    Expands relative audio files to a given `audio_root` path.
    """
    # MODEL = Observation

    def __init__(self, observations, audio_root='', strict=False):
        """
        Parameters
        ----------
        observations : list
            List of Observations (as dicts or Observations.)
            If they're dicts, this will convert them to Observations.

        data_root : str or None
            Path to look for an observation, if not None
        """
        self._observations = [Observation(**_enforce_obs(x, audio_root,
                                                         strict))
                              for x in observations]
        self.audio_root = audio_root
        self.strict = strict

    def __eq__(self, a):
        is_eq = False
        if hasattr(a, 'to_builtin'):
            is_eq = self.to_builtin() == a.to_builtin()
        return is_eq

    def __len__(self):
        return len(self.values())

    def __getitem__(self, n):
        """Return the observation for a given integer index."""
        return self._observations[n]

    def items(self):
        return [(v.index, v) for v in self.values()]

    def values(self):
        return self._observations

    def keys(self):
        return [v.index for v in self.values()]

    def append(self, observation, audio_root=None):
        audio_root = self.audio_root if audio_root is None else audio_root
        obs = _enforce_obs(observation, audio_root, self.strict)
        self._observations += [Observation(**obs)]

    def to_builtin(self):
        return [v.to_builtin() for v in self.values()]

    @classmethod
    def read_json(cls, json_path, audio_root=''):
        with open(json_path, 'r') as fh:
            return cls(json.load(fh), audio_root=audio_root)

    def to_json(self, json_path=None, **kwargs):
        """Pandas-like `to_json` method.

        Parameters
        ----------
        json_path : str, or None
            If given, will attempt to write JSON to disk; else returns a string
            of serialized data.

        **kwargs : keyword args
            Pass-through parameters to the JSON serializer.
        """
        sdata = json.dumps(self.to_builtin(), **kwargs)
        if json_path is not None:
            with open(json_path, 'w') as fh:
                fh.write(sdata)
        else:
            return sdata

    def validate(self, verbose=False, check_files=True):
        """Returns True if all are valid."""
        return all([x.validate(verbose=verbose, check_files=check_files)
                    for x in self.values()])

    def to_dataframe(self):
        return pd.DataFrame([x.to_series() for x in self.values()])

    @classmethod
    def from_dataframe(cls, dframe, audio_root=''):
        return cls([Observation.from_series(x) for _, x in dframe.iterrows()],
                   audio_root=audio_root)

    def copy(self, deep=True):
        return Collection(copy.deepcopy(self._observations))

    def view(self, column, filter_value):
        """Returns a copy of the collection restricted to the filter value.

        Parameters
        ----------
        column : str
            Name of the column for filtering.

        filter_value : obj
            Value to restrict the collection.

        Returns
        -------

        """
        thecopy = copy.copy(self.to_dataframe())
        ds_view = thecopy[thecopy[column] == filter_value]
        return Collection.from_dataframe(ds_view, self.audio_root)


def load(filename, audio_root):
    """
    """
    return Collection.load(filename)


def partition_collection(collection, test_set, train_val_split=0.2,
                         max_files_per_class=None):
    """Returns Datasets for train and validation constructed
    from the datasets not in the test_set, and split with
    the ratio train_val_split.

     * First selects from only the datasets given in datasets.
     * Then **for each instrument** (so the distribution from
         each instrument doesn't change)
        * train_test_split to generate training and validation sets.
        * if max_files_per_class, also then restrict the training set to
            a maximum of that number of files for each train and test

    Parameters
    ----------
    test_set : str
        String in ["rwc", "uiowa", "philharmonia"] which selects
        the hold-out-set to be used for testing.

    Returns
    -------
    partition_df : pd.DataFrame
        DataFrame with only an index to the original table, and
        the partiition in ['train', 'valid', 'test']
    """
    df = collection.to_dataframe()
    df_test = collection.view(
        column='dataset', filter_value=test_set).to_dataframe()
    datasets = set(df["dataset"].unique()) - set([test_set])
    search_df = df[df["dataset"].isin(datasets)]

    selected_instruments_train = []
    selected_instruments_valid = []
    for instrument in search_df["instrument"].unique():
        instrument_df = search_df[search_df["instrument"] == instrument]

        if len(instrument_df) < 2:
            logger.warning("Instrument {} doesn't haven enough samples "
                           "to split.".format(instrument))
            continue

        traindf, validdf = train_test_split(
            instrument_df, test_size=train_val_split)

        if max_files_per_class:
            replace = False if len(traindf) > max_files_per_class else True
            traindf = traindf.sample(n=max_files_per_class,
                                     replace=replace)

        selected_instruments_train.append(traindf)
        selected_instruments_valid.append(validdf)

    train_df = pd.concat(selected_instruments_train)
    valid_df = pd.concat(selected_instruments_valid)

    # Create the final dataframe
    partition = (['train'] * len(train_df) +
                 ['valid'] * len(valid_df) +
                 ['test'] * len(df_test))

    index = (train_df.index +
             valid_df.index +
             df_test.index)

    result = pd.DataFrame(partition,
                          columns=['partition'],
                          index=index)
    return result
