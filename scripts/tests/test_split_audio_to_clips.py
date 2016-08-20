import pytest

import os
import pandas as pd

import minst.utils as utils
import split_audio_to_clips as SC


def test_module():
    assert SC is not None


def test_audio_to_observations(uiowa_root, onset_root, workspace):
    audio_file = os.path.join(
        uiowa_root, "theremin.music.uiowa.edu/sound files/MIS/Brass/tuba"
                    "/Tuba.ff.C3C4.aiff")
    assert os.path.exists(audio_file)
    index = "uiowa78fae0a0"
    onset_file = os.path.join(onset_root, 'uiowa', "{}.csv".format(index))
    assert os.path.exists(onset_file)

    output_dir = os.path.join(workspace, 'notes_tmp')
    utils.create_directory(output_dir)

    fext = 'flac'
    observations = SC.audio_to_observations(
        index, audio_file, onset_file, output_dir, file_ext=fext,
        instrument='Tuba', dataset='uiowa')

    onset_df = pd.read_csv(onset_file)
    assert len(observations) == len(onset_df)
    for obs in observations:
        obs.instrument == 'Tuba'

    assert len(set([obs.index for obs in observations])) == len(observations)
