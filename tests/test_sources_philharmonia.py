import pytest
import os

import helpers
import minst.sources.philharmonia as philz


def test_philz_instrument_code_to_name():
    # We'll just test a few.
    test_pairs = [("AS", "saxophone-alto"),
                  ("FG", "bassoon"),
                  ("TB", "trombone"),
                  # No valid mapping should produce None
                  ("SZ", None),
                  ("what", None)]

    for value, expected in test_pairs:
        result = philz.instrument_code_to_name(value)
        yield helpers.__test, result, expected


def test_philz_parse():
    test_pairs = [("011PFNOF.flac", ("piano", "NO", "F")),
                  ("232TUNOF.flac", ("tuba", "NO", "F")),
                  ("472TNA1F", (None, "A1", "F"))]

    for value, expected in test_pairs:
        result = philz.parse(value)
        yield helpers.__test, result, expected


def test_philz_collect():
    """Test that an input folder with files in rwc format is correctly
    converted to a dataframe."""
    philz_dir = os.path.join(os.path.dirname(__file__), 'dummy_philharmonia')

    philz_df = philz.collect(philz_dir)
    yield helpers.__test_df_has_data, philz_df
    yield helpers.__test_pd_output, philz_df, philz.NAME
