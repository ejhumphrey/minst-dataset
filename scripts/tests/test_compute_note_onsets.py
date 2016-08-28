import pytest

import os
import pandas as pd

import compute_note_onsets as CNO


def test_compute_note_onsets_import():
    assert CNO is not None


def test_segment_one(audio_file, workspace):
    idx = 'blahblah'
    output_file = CNO.segment_one(idx, audio_file, 'envelope', workspace)
    assert os.path.exists(output_file)


def test_segment_many(audio_file, workspace):
    idxs = ['blahblahlaksdjf', 'yippeekjasdfklj']
    output_files = CNO.segment_many(
        index=idxs, audio_files=[audio_file] * 2,
        mode='envelope', output_directory=workspace, num_cpus=1)
    for fout in output_files:
        assert os.path.exists(fout)

    with pytest.raises(ValueError):
        CNO.segment_many(
            index=['a'] * 2, audio_files=[audio_file] * 2,
            mode='envelope', output_directory=workspace, num_cpus=1)


def test_main(audio_file, workspace):
    df = pd.DataFrame.from_records(
        [dict(audio_file=audio_file) for n in range(2)],
        index=['kjhadsfjkha', 'biuhc8y298i8ahsc'])
    index_file = os.path.join(workspace, 'test_compute_note_onsets_input.csv')
    df.to_csv(index_file, index_col=0)

    index_out = os.path.join(workspace, 'test_compute_note_onsets_output.csv')
    success = CNO.main(index_file, workspace, index_out, mode='envelope',
                       # Some parallelization funniness with librosa?
                       num_cpus=1)
    assert success
