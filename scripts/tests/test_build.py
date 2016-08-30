import pytest

import logging
import os
import pandas as pd

import scripts_helpers

import minst.logger
import minst.sources.uiowa as uiowa
import minst.sources.rwc as rwc
import minst.sources.philharmonia as philz

logging.config.dictConfig(minst.logger.get_config('INFO'))


def test_build_default_uiowa(workspace, uiowa_root):
    notes_dir = os.path.join(workspace, 'notes_dir')
    notes_index = scripts_helpers.build_with_default_onsets(
        'uiowa', workspace, notes_dir, uiowa_root)

    notes = pd.read_csv(notes_index)
    assert len(notes) == 49


def test_build_default_rwc(workspace, rwc_root):
    notes_dir = os.path.join(workspace, 'notes_dir')
    notes_index = scripts_helpers.build_with_default_onsets(
        'rwc', workspace, notes_dir, rwc_root)
    notes = pd.read_csv(notes_index)
    assert len(notes) == 191


def test_build_default_philharmonia(workspace, philz_root):
    notes_dir = os.path.join(workspace, 'notes_dir')
    notes_index = scripts_helpers.build_with_default_onsets(
        'philharmonia', workspace, notes_dir, philz_root)

    notes = pd.read_csv(notes_index)
    assert len(notes) == 19
