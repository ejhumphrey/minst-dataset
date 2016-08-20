import pytest

import os
import pandas as pd

import minst.utils as utils
import split_audio_to_clips as SC


def test_module():
    assert SC is not None


def test_split_audio_with_onsets(uiowa_root, onset_root, workspace):
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
    notes = SC.split_audio_with_onsets(audio_file, onset_file,
                                       output_dir, file_ext=fext)

    onset_df = pd.read_csv(onset_file)
    assert len(notes) == len(onset_df)
