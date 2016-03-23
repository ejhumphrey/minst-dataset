import pytest
import os

import helpers
import minst.sources.uiowa as U


def test_uiowa_parse():
    test_pairs = [("Horn.ff.Bb1B1.aiff", ("Horn", "ff", "Bb1B1")),
                  ("Cello.arco.ff.sulA.C4B4.aiff", ("Cello", "ff", "C4B4")),
                  ("Viola.arco.sulA.ff.A4B4.aiff", ("Viola", "ff", "A4B4")),
                  ("Rubber.aif", ("Rubber", None, None)),
                  ("Guitar.ff.sul_E.C5Bb5.stereo.aif",
                   ("Guitar", "ff", "C5Bb5")),
                  ("Piano.ff.B3.aiff", ("Piano", "ff", "B3")),
                  ("Trumpet.vib.ff.E3B3.aiff", ("Trumpet", "ff", "E3B3"))]

    for value, expected in test_pairs:
        yield helpers.__test, U.parse(value), expected


def test_uiowa_num_notes_from_filename():
    test_pairs = [("Horn.ff.Bb1B1.aiff", 2),
                  ("Cello.arco.ff.sulA.C4B4.aiff", 12),
                  ("Viola.arco.sulA.ff.A4B4.aiff", 3),
                  ("Rubber.aif", None),
                  ("Guitar.ff.sul_E.C5Bb5.stereo.aif", 11),
                  ("Piano.ff.B3.aiff", 1),
                  ("Trumpet.vib.ff.E3B3.aiff", 8)]

    for value, expected in test_pairs:
        result = U.num_notes_from_filename(value)
        yield helpers.__test, result, expected


def test_uiowa_collect():
    """Test that an input folder with files in uiowa format is correctly
    converted to a dataframe."""
    uiowa_dir = os.path.join(os.path.dirname(__file__), 'dummy_uiowa')
    uiowa_df = U.collect(uiowa_dir)
    yield helpers.__test_df_has_data, uiowa_df
    yield helpers.__test_pd_output, uiowa_df, "uiowa"
