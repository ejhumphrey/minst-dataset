import pytest
import numpy as np
import os

import minst.taxonomy as tax
import minst.sources.rwc as RWC


def __test(value, expected):
    assert value == expected


def __test_df_has_data(df):
    assert not df.empty


def __test_pd_output(pd_output, dataset):
    """Make sure all the files in the tree exist"""
    # Check for valid columns
    required_columns = ['audio_file', 'dataset', 'instrument', 'dynamic']
    for column in required_columns:
        assert column in pd_output.columns

    # Check files and per row things.
    for row in pd_output.iterrows():
        assert os.path.exists(row[1]['audio_file'])
        assert row[1]['dataset'] == dataset

    classmap = tax.InstrumentClassMap()

    # Make sure we have all the selected instruments
    instruments = pd_output["instrument"].unique()
    map_inst = [classmap[x] for x in instruments if classmap[x]]
    inst_found = np.array([(x in classmap.classnames) for x in map_inst])
    assert all(inst_found), "Dataset {} is missing: {}".format(
        dataset, inst_found[inst_found == 0])


def test_rwc_instrument_code_to_name():
    # We'll just test a few.
    test_pairs = [("AS", "saxophone-alto"),
                  ("FG", "bassoon"),
                  ("TB", "trombone"),
                  # No valid mapping should produce None
                  ("SZ", None),
                  ("what", None)]

    for value, expected in test_pairs:
        result = RWC.instrument_code_to_name(value)
        yield __test, result, expected


def test_rwc_parse():
    test_pairs = [("011PFNOF.flac", ("piano", "NO", "F")),
                  ("232TUNOF.flac", ("tuba", "NO", "F")),
                  ("472TNA1F", (None, "A1", "F"))]

    for value, expected in test_pairs:
        result = RWC.parse(value)
        yield __test, result, expected


def test_rwc_collect():
    """Test that an input folder with files in rwc format is correctly
    converted to a dataframe."""
    rwc_dir = os.path.join(os.path.dirname(__file__), 'dummy_rwc')

    rwc_df = RWC.collect(rwc_dir)
    yield __test_df_has_data, rwc_df
    yield __test_pd_output, rwc_df, "rwc"
