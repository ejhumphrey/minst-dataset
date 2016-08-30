import pytest
import logging
import os
import pandas as pd

import collect_data
import minst.logger
import minst.sources.uiowa as uiowa
# import minst.sources.rwc as rwc
# import minst.sources.philharmonia as philz
import split_audio_to_clips
import compute_note_onsets

logging.config.dictConfig(minst.logger.get_config('INFO'))


def build_dataset(dataset, output_dir, data_root):
    dset_index = os.path.join(output_dir, "{}_index.csv".format(dataset))
    collect_data.build_index(
        dataset, data_root, dset_index, strict_taxonomy=True)

    segment_dir = os.path.join(output_dir, '{}_segments'.format(dataset))
    segment_index = os.path.join(output_dir,
                                 "{}_segment_index.csv".format(dataset))
    compute_note_onsets.main(
        dset_index, segment_dir, segment_index,
        mode='envelope', num_cpus=1, verbose=20)

    notes_index = os.path.join(output_dir,
                               "{}_notes_index.csv".format(dataset))
    notes_dir = os.path.join(output_dir, '{}_notes'.format(dataset))
    split_audio_to_clips.audio_collection_to_observations(
        segment_index, notes_index, notes_dir)

    return segment_dir, segment_index, notes_index


def test_build_uiowa(workspace, uiowa_root):
    expected_index = ['uiowa78fae0a0', 'uiowa095def27']
    segment_dir, segment_index, notes_index = build_dataset(
        'uiowa', workspace, uiowa_root)

    segments = pd.read_csv(segment_index, index_col=0)
    for ix in expected_index:
        assert ix in segments.index
    assert segments.ix[0].onsets_file

    uiowa_index = uiowa.collect(uiowa_root, onset_dir=segment_dir)

    for ix in expected_index:
        assert ix in uiowa_index.index
    assert uiowa_index.to_dict() == segments.to_dict()

    notes = pd.read_csv(notes_index)
    print("loaded notes: \n{}".format(notes))
    assert len(notes) == 13
