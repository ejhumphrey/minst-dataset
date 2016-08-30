import pytest

import logging
import pandas as pd

import scripts_helpers

import minst.logger
import minst.sources.uiowa as uiowa
import minst.sources.rwc as rwc
import minst.sources.philharmonia as philz

logging.config.dictConfig(minst.logger.get_config('INFO'))


def test_build_default_uiowa(workspace, uiowa_root):
    notes_index, notes_dir = scripts_helpers.build_with_default_onsets(
        'uiowa', workspace, uiowa_root)

    notes = pd.read_csv(notes_index)
    assert len(notes) == 49


def test_build_default_rwc(workspace, rwc_root):
    notes_index, notes_dir = scripts_helpers.build_with_default_onsets(
        'rwc', workspace, rwc_root)
    notes = pd.read_csv(notes_index)
    assert len(notes) == 191


def test_build_default_philharmonia(workspace, philz_root):
    notes_index, notes_dir = scripts_helpers.build_with_default_onsets(
        'philharmonia', workspace, philz_root)

    notes = pd.read_csv(notes_index)
    assert len(notes) == 19
