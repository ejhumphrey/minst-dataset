import os

import collect_data
import split_audio_to_clips
import compute_note_onsets


def build_dataset(dataset, output_dir, data_root):
    dset_index = os.path.join(output_dir, "{}_index.csv".format(dataset))
    collect_data.build_index(
        dataset, data_root, dset_index, strict_taxonomy=True)

    segment_dir = os.path.join(output_dir, '{}_segments'.format(dataset))
    segment_index = os.path.join(output_dir,
                                 "{}_segment_index.csv".format(dataset))
    compute_note_onsets.main(
        dset_index, segment_dir, segment_index,
        mode='envelope', num_cpus=1, verbose=20)

    notes_index = os.path.join(output_dir,
                               "{}_notes_index.csv".format(dataset))
    notes_dir = os.path.join(output_dir, '{}_notes'.format(dataset))
    split_audio_to_clips.audio_collection_to_observations(
        segment_index, notes_index, notes_dir)

    return segment_dir, segment_index, notes_index
