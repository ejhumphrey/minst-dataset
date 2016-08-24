import pytest

import os
import pandas as pd

import minst.model as model


@pytest.fixture
def rwc_obs():
    return dict(index='U1309f091', dataset='uiowa',
                audio_file="RWC_I_01/011/011PFNOP.flac",
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


def test_Observation___init__(rwc_obs):
    obs = model.Observation(**rwc_obs)
    assert obs


def test_Observation_to_builtin(rwc_obs):
    obs = model.Observation(**rwc_obs)
    assert obs.to_builtin() == rwc_obs


def test_Observation_from_series(test_obs):
    index = [x.pop('index') for x in test_obs]
    df = pd.DataFrame.from_records(test_obs, index=index)
    # import pdb;pdb.set_trace()
    obs = model.Observation.from_series(df.ix[0])
    assert obs.index == index[0]
    assert obs.instrument == 'tuba'


def test_Observation_to_series(rwc_obs):
    obs = model.Observation(**rwc_obs)
    rec = obs.to_series()
    assert rec.name == rwc_obs['index']
    assert rec.instrument == rwc_obs['instrument']


def test_Observation_to_dict(rwc_obs):
    obs = model.Observation(**rwc_obs)
    rec_obs = obs.to_dict()
    assert rec_obs == rwc_obs


def test_Observation___get_item__(rwc_obs):
    obs = model.Observation(**rwc_obs)
    assert obs['index'] == obs.index == rwc_obs['index']


def test_Observation_validate(rwc_root, rwc_obs, test_obs):
    obs = model.Observation(**rwc_obs)
    assert obs.SCHEMA
    assert not obs.validate()
    assert obs.validate(check_files=False)

    rwc_obs['audio_file'] = os.path.join(rwc_root, rwc_obs['audio_file'])
    obs = model.Observation(**rwc_obs)
    assert obs.validate()

    rwc_obs['audio_file'] = ("dummy_philharmonia/www.philharmonia.co.uk/"
                             "assets/audio/samples/instruments/cello.zip")
    obs = model.Observation(**rwc_obs)
    assert not obs.validate()

    for o in test_obs:
        assert model.Observation(**o).validate(verbose=True, check_files=False)


def test__enforce_obs(rwc_obs, rwc_root):
    obs = model._enforce_obs(rwc_obs, strict=False)
    assert obs is not None

    with pytest.raises(model.MissingDataException):
        model._enforce_obs(rwc_obs, strict=True)

    obs = model._enforce_obs(rwc_obs, audio_root=rwc_root, strict=False)
    assert obs is not None


def test_Collection___init__(test_obs, rwc_obs, rwc_root):
    dset = model.Collection(test_obs)
    assert dset is not None

    with pytest.raises(model.MissingDataException):
        dset = model.Collection(test_obs, strict=True)

    obs = model.Observation(**rwc_obs)
    with pytest.raises(model.MissingDataException):
        dset = model.Collection([obs], audio_root='', strict=True)

    dset = model.Collection([obs], audio_root=rwc_root, strict=True)
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


def test_Collection_append(test_obs, rwc_obs):
    dset = model.Collection(test_obs)
    assert len(dset) == len(test_obs)
    dset.append(rwc_obs)
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


def test_Collection_validate(test_obs, rwc_obs):
    dset = model.Collection(test_obs)
    assert dset.validate(verbose=True, check_files=False)

    rwc_obs['duration'] = 'abcdef'
    dset.append(rwc_obs)
    assert not dset.validate(verbose=True)


def test_Collection_to_dataframe(test_obs):
    dset = model.Collection(test_obs).to_dataframe()
    assert len(dset) == 3
    assert dset.index[0] == test_obs[0]['index']


def test_Collection_from_dataframe(test_obs):
    index = [x.pop('index') for x in test_obs]
    df = pd.DataFrame.from_records(test_obs, index=index)
    dset = model.Collection.from_dataframe(df)
    assert len(dset) == 3
    assert df.ix[0].name == dset[0].index


def test_Collection_view(test_obs):
    ds = model.Collection(test_obs)
    rwc_view = ds.view(column='dataset', filter_value="rwc").to_dataframe()
    assert set(rwc_view["dataset"].unique()) == set(["rwc"])


def test_partition_collection(test_obs):
    dset = model.Collection(test_obs * 10)
    train, valid, test = model.partition_collection(
        dset, test_set='rwc', train_val_split=0.5)
    assert len(train) == len(valid) == len(test) == 10
