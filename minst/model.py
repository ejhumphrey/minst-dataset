
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

    def __init__(self, index, dataset, audio_file, instrument, source_key,
                 start_time, duration, note_number, dynamic, partition,
                 features=None):
        self.index = index
        self.dataset = dataset
        self.audio_file = audio_file
        self.instrument = instrument
        self.source_key = source_key
        self.start_time = start_time
        self.duration = duration
        self.note_number = note_number
        self.dynamic = dynamic
        self.partition = partition
        self.features = features if features else dict()

    def to_builtin(self):
        return self.__dict__.copy()

    def validate(self, schema=None):
        schema = self.SCHEMA if schema is None else schema
        success = True
        try:
            jsonschema.validate(self.to_builtin(), schema)
        except jsonschema.ValidationError:
            success = False
        success &= os.path.exists(self.audio_file)
        if success:
            success &= utils.check_audio_file(self.audio_file)[0]

        return success


class Collection(object):
    def __init__(self, values):
        self._values = [Observation(**v) for v in values]

    def items(self):
        return [(v.index, v) for v in self._values]

    def values(self):
        return self._values

    def keys(self):
        return [v.index for v in self._values]

    def to_builtin(self):
        return [v.to_builtin() for v in self.values()]

    @classmethod
    def load(cls, filename):
        return cls(**json.load(open(filename)))

    def save(self, filename, **kwargs):
        with open(filename) as fp:
            json.dump(self.values(), fp)

    def validate(self):
        return any([o.validate() for o in self.values()])

    def to_dataframe(self):
        pass

    def from_dataframe(self, dframe):
        pass


def load(filename):
    """
    """
    return Collection.load(filename)
