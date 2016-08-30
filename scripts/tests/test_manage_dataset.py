import pytest
import os
import pandas as pd
import random

import minst.model
import minst.sources

import scripts_helpers
import manage_dataset as M


def test_join_note_files(workspace, uiowa_root, rwc_root):

    fpaths = []
    for dset, base_dir in zip(['uiowa', 'rwc'], [uiowa_root, rwc_root]):
        df = minst.sources.SOURCES[dset].collect(base_dir)
        fout = os.path.join(workspace, "join_note_files_{}.csv".format(dset))
        df.to_csv(fout)
        fpaths += [fout]

    assert M.join_note_files(
        fpaths, os.path.join(workspace, 'joined_file.csv'))


def test_train_test_split(workspace, uiowa_root, rwc_root, philz_root):
    datasets = ['a', 'b', 'c']
    observations = []
    for n in range(100):
        dset = random.sample(datasets, 1)[0]
        obs = minst.model.Observation(
            index="{}-{}".format(dset, n),
            dataset=dset, audio_file='blah', instrument='foo',
            source_index="{}{}".format(dset, n % 5), start_time=0,
            duration=1.0)
        observations += [obs]
    collec = minst.model.Collection(observations, strict=False)

    note_index = os.path.join(workspace, 'train_test_split_note_index.csv')
    collec.to_dataframe().to_csv(note_index)

    partition_index = os.path.join(workspace, 'train_test_split_output.csv')
    assert M.train_test_split(note_index, 'c', 0.2, partition_index)


def test_create_example_dataset(workspace, uiowa_root, rwc_root, philz_root):
    notes_dir = os.path.join(workspace, 'notes_data')
    uiowa_notes_index = scripts_helpers.build_with_default_onsets(
        'uiowa', workspace, notes_dir, uiowa_root)
    rwc_notes_index = scripts_helpers.build_with_default_onsets(
        'rwc', workspace, notes_dir, rwc_root)
    philz_notes_index = scripts_helpers.build_with_default_onsets(
        'philharmonia', workspace, notes_dir, philz_root)

    example_dir = os.path.join(workspace, 'example_data')
    source_indexes = [uiowa_notes_index, rwc_notes_index, philz_notes_index]
    master_index = "master_index.csv"
    assert M.create_example_dataset(
        example_dir, source_indexes, notes_dir,
        n_per_instrument=4, output_index=master_index)

    df = pd.read_csv(os.path.join(example_dir, master_index))
    assert len(df) == 24
