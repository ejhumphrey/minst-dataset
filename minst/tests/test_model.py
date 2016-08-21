import pytest

import os
import pandas as pd

import minst.model as model


@pytest.fixture
def raw_obs(rwc_root):
    afile = os.path.join(rwc_root, "RWC_I_01/011/011PFNOP.flac")
    return dict(index='U1309f091', dataset='uiowa', audio_file=afile,
                instrument='piano', source_index='U12345',
                start_time=0.0, duration=2, note_number=45,
                dynamic='pp', partition='test-0')


@pytest.fixture
def test_obs():
    obs = [
        dict(index="abc123", dataset="rwc", audio_file="foo_00.aiff",
             instrument="tuba", source_index="001", start_time=0.0,
             duration=1.0, note_number=None, dynamic="pp", partition=None),
        dict(index="abc234", dataset="uiowa", audio_file="foo_01.aiff",
             instrument="horn-french", source_index="001", start_time=0.0,
             duration=1.0, note_number=None, dynamic="pp", partition=None),
        dict(index="def123", dataset="philharmonia", audio_file="foo_02.aiff",
             instrument="tuba", source_index="001", start_time=0.0,
             duration=1.0, note_number=None, dynamic="pp", partition=None)
    ]
    return obs


def test_Observation___init__(raw_obs):
    obs = model.Observation(**raw_obs)
    assert obs


def test_Observation_to_builtin(raw_obs):
    obs = model.Observation(**raw_obs)
    assert obs.to_builtin() == raw_obs


def test_Observation_from_series(test_obs):
    index = [x.pop('index') for x in test_obs]
    df = pd.DataFrame.from_records(test_obs, index=index)
    # import pdb;pdb.set_trace()
    obs = model.Observation.from_series(df.ix[0])
    assert obs.index == index[0]
    assert obs.instrument == 'tuba'


def test_Observation_to_series(raw_obs):
    obs = model.Observation(**raw_obs)
    rec = obs.to_series()
    assert rec.name == raw_obs['index']
    assert rec.instrument == raw_obs['instrument']


def test_Observation_to_dict(raw_obs):
    obs = model.Observation(**raw_obs)
    rec_obs = obs.to_dict()
    assert rec_obs == raw_obs


def test_Observation___get_item__(raw_obs):
    obs = model.Observation(**raw_obs)
    assert obs['index'] == obs.index == raw_obs['index']


def test_Observation_validate(raw_obs, test_obs):
    obs = model.Observation(**raw_obs)
    assert obs.SCHEMA

    assert obs.validate()
    raw_obs['audio_file'] = ("dummy_philharmonia/www.philharmonia.co.uk/"
                             "assets/audio/samples/instruments/cello.zip")
    obs = model.Observation(**raw_obs)
    assert not obs.validate()

    for o in test_obs:
        assert model.Observation(**o).validate(verbose=True, check_files=False)


def test_Collection___init__(test_obs):
    dset = model.Collection(test_obs)
    assert dset is not None


def test_Collection___len__(test_obs):
    dset = model.Collection(test_obs)
    assert len(dset) == len(test_obs)


def test_Collection___eq__(test_obs):
    dset = model.Collection(test_obs)
    dset2 = model.Collection(test_obs)
    assert dset == dset2
    assert dset != test_obs
    assert dset is not None


def test_Collection_items(test_obs):
    dset = model.Collection(test_obs)
    items = dset.items()
    assert len(items) == len(test_obs)
    assert [x[0] for x in items] == [y['index'] for y in test_obs]


def test_Collection_append(test_obs, raw_obs):
    dset = model.Collection(test_obs)
    assert len(dset) == len(test_obs)
    dset.append(raw_obs)
    assert len(dset) == len(test_obs) + 1


def test_Collection_to_builtin(test_obs):
    dset = model.Collection(test_obs)
    rec_obs = dset.to_builtin()
    assert rec_obs == test_obs


def test_Collection_to_read_json(test_obs, workspace):
    dset = model.Collection(test_obs)
    json_path = os.path.join(workspace, "dummy_collection.json")
    sdata = dset.to_json()
    assert sdata is not None
    dset.to_json(json_path)
    new_dset = dset.read_json(json_path)
    assert dset == new_dset


def test_Collection_validate(test_obs, raw_obs):
    dset = model.Collection(test_obs)
    assert dset.validate(verbose=True, check_files=False)

    raw_obs['duration'] = 'abcdef'
    dset.append(raw_obs)
    assert not dset.validate(verbose=True)


def test_Collection_to_dataframe(test_obs):
    dset = model.Collection(test_obs).to_dataframe()
    assert len(dset) == 3
    assert dset.index[0] == test_obs[0]['index']


def test_Collection_view(test_obs):
    ds = model.Collection(test_obs)
    rwc_view = ds.view("rwc")
    assert set(rwc_view["dataset"].unique()) == set(["rwc"])
