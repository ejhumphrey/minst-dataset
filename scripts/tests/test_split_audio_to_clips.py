import pytest

import os
import pandas as pd

import minst.model as model
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
    onsets_file = os.path.join(onset_root, 'uiowa', "{}.csv".format(index))
    assert os.path.exists(onsets_file)

    output_dir = os.path.join(workspace, 'notes_tmp')
    utils.create_directory(output_dir)

    fext = 'flac'
    observations = SC.audio_to_observations(
        index, audio_file, onsets_file, output_dir, file_ext=fext,
        instrument='Tuba', dataset='uiowa')

    onset_df = pd.read_csv(onsets_file)
    assert len(observations) == len(onset_df)

    coll = model.Collection(observations, output_dir)
    assert coll.validate(verbose=True)
    for obs in coll.values():
        obs.instrument == 'Tuba'

    assert len(set([obs.index for obs in observations])) == len(observations)


def test_audio_collection_to_observations(uiowa_root, onset_root, workspace):
    audio_file = os.path.join(
        uiowa_root, "theremin.music.uiowa.edu/sound files/MIS/Brass/tuba"
                    "/Tuba.ff.C3C4.aiff")
    assert os.path.exists(audio_file)
    index = "uiowa78fae0a0"
    onsets_file = os.path.join(onset_root, 'uiowa', "{}.csv".format(index))
    assert os.path.exists(onsets_file)

    output_dir = os.path.join(workspace, 'notes_tmp')
    utils.create_directory(output_dir)

    rec = dict(audio_file=audio_file, onsets_file=onsets_file,
               instrument="Tuba", dataset='uiowa', dynamic='ff')
    seg_index = pd.DataFrame.from_records([rec], index=[index])
    seg_file = os.path.join(workspace, 'seg_index.csv')
    seg_index.to_csv(seg_file)

    assert SC.audio_collection_to_observations(
        seg_file, 'successful_note_index.csv', output_dir)


def test_audio_collection_to_observations_no_onsets(uiowa_root, workspace):
    audio_file = os.path.join(
        uiowa_root, "theremin.music.uiowa.edu/sound files/MIS/Brass/tuba"
                    "/Tuba.ff.C3C4.aiff")
    assert os.path.exists(audio_file)
    index = "uiowa78fae0a0"

    output_dir = os.path.join(workspace, 'notes_tmp')
    utils.create_directory(output_dir)

    rec = dict(audio_file=audio_file, onsets_file=None,
               instrument="Tuba", dataset='uiowa', dynamic='ff')
    seg_index = pd.DataFrame.from_records([rec], index=[index])
    seg_file = os.path.join(workspace, 'seg_index.csv')
    seg_index.to_csv(seg_file)

    assert SC.audio_collection_to_observations(
        seg_file, 'empty_note_index.csv', output_dir)
