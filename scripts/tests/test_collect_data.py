import pytest

import os

import collect_data as CD


def test_collect_data_import():
    assert CD is not None


def test_build_index_rwc(rwc_root, workspace):
    name = 'rwc'
    output_file = os.path.join(workspace,
                               "test_build_index_{}.csv".format(name))
    assert CD.build_index(name, rwc_root, output_file, strict_taxonomy=True)


def test_build_index_uiowa(uiowa_root, workspace):
    name = 'uiowa'
    output_file = os.path.join(workspace,
                               "test_build_index_{}.csv".format(name))
    assert CD.build_index(name, uiowa_root, output_file, strict_taxonomy=True)


def test_build_index_philharmonia(philz_root, workspace):
    name = 'philharmonia'
    output_file = os.path.join(workspace,
                               "test_build_index_{}.csv".format(name))
    assert CD.build_index(name, philz_root, output_file,
                          strict_taxonomy=True)


def test_build_index_good_sounds(goodsounds_root, workspace):
    name = 'good-sounds'
    output_file = os.path.join(workspace,
                               "test_build_index_{}.csv".format(name))
    assert CD.build_index(name, goodsounds_root, output_file,
                          strict_taxonomy=True)
