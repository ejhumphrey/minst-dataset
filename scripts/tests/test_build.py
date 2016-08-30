import pytest

import logging
import pandas as pd

import scripts_helpers
import minst.logger
import minst.sources.uiowa as uiowa
# import minst.sources.rwc as rwc
# import minst.sources.philharmonia as philz

logging.config.dictConfig(minst.logger.get_config('INFO'))


def test_build_uiowa(workspace, uiowa_root):
    expected_index = ['uiowa78fae0a0', 'uiowa095def27']
    segment_dir, segment_index, notes_index = scripts_helpers.build_dataset(
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
