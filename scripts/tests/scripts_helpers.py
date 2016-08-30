import pytest

import boltons.fileutils
import os
import pandas as pd

import minst.sources

import collect_data
import split_audio_to_clips
import compute_note_onsets


def build_with_default_onsets(dataset, output_dir, data_root):
    dset_index = os.path.join(output_dir, "{}_index.csv".format(dataset))
    collect_data.build_index(
        dataset, data_root, dset_index, strict_taxonomy=True)

    notes_index = os.path.join(output_dir,
                               "{}_notes_index.csv".format(dataset))
    notes_dir = os.path.join(output_dir, '{}_notes'.format(dataset))
    boltons.fileutils.mkdir_p(notes_dir)

    df = pd.read_csv(dset_index, index_col=0)
    if df.empty:
        import ipdb;ipdb.set_trace()

    split_audio_to_clips.audio_collection_to_observations(
        dset_index, notes_index, notes_dir)

    return notes_index, notes_dir
