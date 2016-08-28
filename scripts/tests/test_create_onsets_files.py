import pytest

import os
import pandas as pd

import create_onsets_files as COF


def test_create_onsets_files_main(workspace):
    df = pd.DataFrame.from_records([dict(a=2)] * 2, index=['a', 'b'])

    index_file = os.path.join(workspace, 'dummy_onsets_file_index.csv')
    df.to_csv(index_file, index_col=0)
    assert COF.main(index_file, workspace)
