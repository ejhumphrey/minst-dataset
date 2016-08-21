import pytest
import logging
import os
import pandas as pd

import collect_data
import minst.logger
import minst.sources.uiowa as uiowa
import split_audio_to_clips
import compute_note_onsets

logging.config.dictConfig(minst.logger.get_config('INFO'))


def test_build_uiowa(workspace, uiowa_root):
    expected_index = ['uiowa78fae0a0', 'uiowa095def27']
    uiowa_index = os.path.join(workspace, "uiowa_index.csv")
    status = collect_data.build_index(
        'uiowa', uiowa_root, uiowa_index, strict_taxonomy=True)
    assert status

    segment_dir = os.path.join(workspace, 'uiowa_segments')
    segment_index = os.path.join(workspace, "uiowa_segment_index.csv")
    status = compute_note_onsets.main(
        uiowa_index, segment_dir, segment_index,
        mode='envelope', num_cpus=1, verbose=20)
    assert status
    segments = pd.read_csv(segment_index, index_col=0)
    print(segments)
    for ix in expected_index:
        assert ix in segments.index
    assert segments.ix[0].onsets_file

    uiowa_index = uiowa.collect(uiowa_root, onset_dir=segment_dir)

    for ix in expected_index:
        assert ix in uiowa_index.index
    assert uiowa_index.to_dict() == segments.to_dict()

    notes_index = os.path.join(workspace, "uiowa_notes_index.csv")
    notes_dir = os.path.join(workspace, 'uiowa_notes')
    success = split_audio_to_clips.audio_collection_to_observations(
        segment_index, notes_index, notes_dir)

    assert success
    # import pdb;pdb.set_trace()

    notes = pd.read_csv(notes_index)
    print("loaded notes: \n{}".format(notes))
    assert len(notes) == 13


@pytest.mark.skipif(True, reason="remove or turn into real mainfile.")
def test_build_uiowa_full():

    uiowa_root = "/Users/ejhumphrey/data/minst/uiowa"
    uiowa_index_file = "/Users/ejhumphrey/data/minst/uiowa_index.csv"
    status = collect_data.build_index(
        'uiowa', uiowa_root, uiowa_index_file, strict_taxonomy=True)
    assert status

    segment_dir = "/Users/ejhumphrey/data/minst/uiowa_segments"
    segment_index = "/Users/ejhumphrey/data/minst/uiowa_segment_index.csv"

    status = compute_note_onsets.main(
        uiowa_index_file, segment_dir, segment_index,
        mode='hll', num_cpus=1, verbose=20)
    assert status
    segments = pd.read_csv(segment_index, index_col=0)

    uiowa_index = uiowa.collect(uiowa_root, onset_dir=segment_dir)
    assert uiowa_index.to_dict() == segments.to_dict()
