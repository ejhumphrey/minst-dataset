import pytest
import os
import numpy as np

import minst.taxonomy as tax


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
