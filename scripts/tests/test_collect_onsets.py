import pytest

import os
import pandas as pd

import collect_onsets as CO


def test_collect_onsets_import():
    assert CO is not None


def test_collect_onsets(workspace, onset_root):
    onsets_df = pd.DataFrame.from_records([dict(time=1.3), dict(time=0.2)])
    onsets_file = os.path.join(workspace, 'dummy_onsets_data-fix.csv')
    onsets_df.to_csv(onsets_file)
    seg_df = pd.DataFrame.from_records(
        [dict(instrument='tuba', logcqt=onsets_file.replace('-fix', ''),
              onsets='placeholder')])

    seg_file = os.path.join(workspace, 'dummy_seg_index.csv')
    seg_df.to_csv(seg_file, index_col=0)
    assert CO.collect_onsets(seg_file, workspace)
