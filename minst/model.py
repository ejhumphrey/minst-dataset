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
    def from_record(cls, record):
        """Convert a record (pd.Series from a DF) to an Observation."""
        return cls(index=record.index[0][0],
                   dataset=record['dataset'][0],
                   audio_file=record['audio_file'][0],
                   instrument=record['instrument'][0],
                   source_key="",
                   start_time=0.0,
                   duration=0.0,
                   note_number=record['note'][0],
                   dynamic=record['dynamic'][0],
                   partition="")

    def to_record(self):
        """Returns the observation as an (index, record) tuple."""
        obj = self.to_builtin()
        index = obj.pop('index')
        return index, obj

    def to_dict(self):
        return self.__dict__.copy()

    def __getitem__(self, key):
        return self.__dict__[key]

    def to_series(self):
        """Convert to a flat series (ie make features a column)

        Returns
        -------
        pandas.Series
        """
        flat_dict = self.to_dict()
        # TODO: necessary?
        flat_dict.update(**flat_dict.pop("features"))
        return pd.Series(flat_dict)

    def validate(self, schema=None, verbose=False):
        schema = self.SCHEMA if schema is None else schema
        success = True
        try:
            jsonschema.validate(self.to_builtin(), schema)
        except jsonschema.ValidationError as derp:
            success = False
            if verbose:
                print("Failed schema test: \n{}".format(derp))
        success &= os.path.exists(self.audio_file)
        if success:
            success &= utils.check_audio_file(self.audio_file)[0]
            if not success and verbose:
                print("Failed file check: \n{}".format(self.audio_file))

        return success


def safe_obs(obs, data_root=None):
    """Get dict from an Observation if an observation, else just dict"""
    if not os.path.exists(obs['audio_file']) and data_root:
        if not os.path.exists(data_root):
            raise MissingDataException(
                "Input data {} missing; have you extracted the zip?")
        new_audio = os.path.join(data_root, obs['audio_file'])
        if os.path.exists(new_audio):
            obs['audio_file'] = new_audio
    if isinstance(obs, Observation):
        return obs.to_dict()
    else:
        return obs


class Collection(object):
    """Expands relative audio files to a given `audio_root` path.
    """
    # MODEL = Observation

    def __init__(self, observations, audio_root=''):
        """
        Parameters
        ----------
        observations : list
            List of Observations (as dicts or Observations.)
            If they're dicts, this will convert them to Observations.

        data_root : str or None
            Path to look for an observation, if not None
        """
        self._observations = [Observation(**safe_obs(x, audio_root))
                              for x in observations]
        self.audio_root = audio_root

    def items(self):
        return [(v.index, v) for v in self.values()]

    def values(self):
        return self._observations

    def keys(self):
        return [v.index for v in self.values()]

    def to_builtin(self):
        return [v.to_builtin() for v in self.values()]

    @classmethod
    def read_json(cls, json_path, data_root=None):
        if os.path.exists(json_path):
            with open(json_path, 'r') as fh:
                return cls(json.load(fh), data_root=data_root)
        else:
            logger.error("No dataset available at {}".format(json_path))
            return None

    def save_json(self, json_path):
        with open(json_path, 'w') as fh:
            json.dump(self.to_builtin(), fh)

    def validate(self, verbose=False):
        return any([x.validate(verbose=verbose) for x in self.values()])

    def to_dataframe(self):
        irecords = [x.to_record() for x in self.values()]
        return pd.DataFrame.from_records(
            [ir[1] for ir in irecords],
            index=[ir[0] for ir in irecords])
        # TODO: prefer CBJ style?
        # return pandas.DataFrame([x.to_series() for x in self.observations])

    def from_dataframe(self, dframe):
        pass

    def __len__(self):
        return len(self.values())

    def __getitem__(self, index):
        return self._observations[index]

    def copy(self, deep=True):
        return Collection(copy.deepcopy(self._observations))

    def view(self, dataset_filter):
        """Returns a copy of the analyzer pointing to the desired dataset.
        Parameters
        ----------
        dataset_filter : str
            String in ["rwc", "uiowa", "philharmonia"] which is
            the items in the dataset to return.

        Returns
        -------
        """
        thecopy = copy.copy(self.to_df())
        ds_view = thecopy[thecopy["dataset"] == dataset_filter]
        return ds_view


def load(filename, audio_root):
    """
    """
    return Collection.load(filename)


def parition(collection, test_set, train_val_split=0.2,
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
    train_df, valid_df, test_df : pandas.DataFrame
        DataFrames of observations for train, validation, and test.
    """
    df = collection.to_dataframe()
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

    return (pd.concat(selected_instruments_train),
            pd.concat(selected_instruments_valid))
