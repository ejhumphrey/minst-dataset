
import json
import jsonschema
import pandas as pd
import os

import minst.utils as utils


class Observation(object):
    """Document model each item in the collection."""

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

    def to_record(self):
        """Returns the observation as an (index, record) tuple."""
        obj = self.to_builtin()
        index = obj.pop('index')
        return index, obj

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


class Collection(object):
    """Expands relative audio files to a given `audio_root` path.
    """
    # MODEL = Observation

    def __init__(self, values, audio_root=''):
        # TODO: Make this a little jamsy
        # self._values = [self.MODEL(**v) for v in values]
        self._values = values
        self.audio_root = audio_root
        for v in self._values:
            v.audio_file = os.path.join(audio_root, v.audio_file)

    def items(self):
        return [(v.index, v) for v in self.values()]

    def values(self):
        return self._values

    def keys(self):
        return [v.index for v in self.values()]

    def to_builtin(self):
        return [v.to_builtin() for v in self.values()]

    @classmethod
    def load(cls, filename):
        return cls(**json.load(open(filename)))

    def save(self, filename, **kwargs):
        with open(filename) as fp:
            json.dump(self.values(), fp)

    def validate(self, verbose=False):
        return any([o.validate(verbose=verbose) for o in self.values()])

    def to_dataframe(self):
        irecords = [obs.to_record() for obs in self.values()]
        return pd.DataFrame.from_records(
            [ir[1] for ir in irecords],
            index=[ir[0] for ir in irecords])

    def from_dataframe(self, dframe):
        pass

    def __len__(self):
        return len(self._values)


def load(filename):
    """
    """
    return Collection.load(filename)
