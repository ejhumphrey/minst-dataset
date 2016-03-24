import pytest
import os

import minst.model as model

DIRNAME = os.path.dirname(__file__)


@pytest.fixture
def raw_obs():
    afile = os.path.join(DIRNAME, "dummy_rwc/RWC_I_01/011/011PFNOP.flac")
    return dict(index='U1309f091', dataset='uiowa', audio_file=afile,
                instrument='piano', source_key='U12345',
                start_time=0.0, duration=2, note_number=45,
                dynamic='pp', partition='test-0')


def test_Observation___init__(raw_obs):
    obs = model.Observation(**raw_obs)
    assert obs


def test_Observation_validate(raw_obs):
    obs = model.Observation(**raw_obs)
    assert obs.SCHEMA

    assert obs.validate()
    raw_obs['audio_file'] = "dummy_philharmonia/www.philharmonia.co.uk/"\
                            "assets/audio/samples/instruments/cello.zip"
    obs = model.Observation(**raw_obs)
    assert not obs.validate()
