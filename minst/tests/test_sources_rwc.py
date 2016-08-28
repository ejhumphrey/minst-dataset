import pytest

import helpers
import minst.sources.rwc as rwc


def test_rwc_instrument_code_to_name():
    # We'll just test a few.
    test_pairs = [("AS", "saxophone-alto"),
                  ("FG", "bassoon"),
                  ("TB", "trombone"),
                  # No valid mapping should produce None
                  ("SZ", None),
                  ("what", None)]

    for value, expected in test_pairs:
        result = rwc.instrument_code_to_name(value)
        yield helpers.__test, result, expected


def test_rwc_parse():
    test_pairs = [("011PFNOF.flac", ("piano", "NO", "F")),
                  ("232TUNOF.flac", ("tuba", "NO", "F")),
                  ("472TNA1F", (None, "A1", "F"))]

    for value, expected in test_pairs:
        result = rwc.parse(value)
        yield helpers.__test, result, expected


def test_rwc_collect(rwc_root):
    """Test that an input folder with files in rwc format is correctly
    converted to a dataframe."""
    rwc_df = rwc.collect(rwc_root)
    helpers.__test_df_has_data(rwc_df)
    helpers.__test_pd_output(rwc_df, rwc.NAME)
    assert 'onsets_file' in rwc_df.columns
    assert len(rwc_df.onsets_file.dropna()) == len(rwc_df)
