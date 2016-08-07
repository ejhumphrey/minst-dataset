"""Using annotated onsets, segment source audio files into individual
audio files, with each containing a single 'note'.

Usage:
 segment_audio.py [options] <segment_index> <note_index> <note_audio_dir>
 segment_audio.py [options] <segment_index> <note_index> <note_audio_dir>
 segment_audio.py [options] <segment_index> <note_index> --pass_thru

Example:

Arguments:
 segment_index   Input index file, as generated by `collect_data.py`.
 note_index      csv file which will contain the record of all notes
                 created.
 note_audio_dir  Directory where note audio will be stored.

Options:
 -h, --help      Print help.
 --dry-run       Don't actually run sox; just print the function call.
 -v, --verbose   Increase verbosity level.
 --pass_thru     Pass through option writes a note_index with the same
                 information as the segment_index without extracting notes.
 --limit=N_FILES  Limit to procesing N_FILES for testing.
"""
from __future__ import print_function
import boltons.fileutils
import claudio
from docopt import docopt
import logging
import logging.config
import os
import pandas as pd
import sys
import time

import minst.logger
import minst.utils as utils

logger = logging.getLogger("segment_audio")

PRINT_PROGRESS = True


def segment_audio_from_onsets(audio_file, onset_file, note_audio_dir,
                              file_ext='flac'):
    """Segment an audio file given an onset file, writing outputs to disk.

    Paramaters
    ----------
    audio_file : str
        Source audio file.

    onset_file : str
        Path to a CSV file of cut points.

    note_audio_dir : str
        Path at which to write outputs.

    Returns
    -------
    note_files : list of str
        Collection of paths on disk of generated outputs. These will take the
        following format:
            {note_audio_dir}/{input_base}_{i}.{file_ext}
    """
    # Get the soxi information on this file to get the Duration
    max_length = float(claudio.sox.soxi(audio_file, 'D'))
    # max_length = file_info['Duration']['seconds']

    # load the onset file.
    onsets = pd.read_csv(onset_file, index_col=0)
    if onsets.empty:
        logger.warning("Onset File is empty! We can't extract notes without "
                       "onsets, so skipping: {}".format(
                        os.path.basename(onset_file)))
        return []

    # Append the duration to the end of the offsets so we can
    # do this by pairs.
    onsets.loc[onsets.size] = max_length

    # Make sure it's sorted by time now.
    onsets = onsets.sort_values('time').reset_index(drop=True)

    new_files = []

    # for each pair of onsets
    for i in range(len(onsets) - 1):
        start_time = onsets.iloc[i]['time']
        if start_time < 0.0:
            start_time = 0.0
        end_time = onsets.iloc[i + 1]['time']
        if end_time > max_length:
            end_time = max_length

        input_base = utils.filebase(audio_file)
        output_file = os.path.join(note_audio_dir, "{}_{}.{}".format(
            input_base, i, file_ext.strip('.')))

        # split to a new file
        success = claudio.sox.trim(
            audio_file, output_file, start_time, end_time)

        if success:
            new_files.append(output_file)

    return new_files


def segment_audio(segment_index_file, note_index_file, note_audio_dir,
                  pass_through=False, limit_n_files=None):
    """
    Parameters
    ----------
    segment_index_file : str
        Input file containing all pointers to audio files and
        onsets files.

    note_index_file: str
        Path to the output index file which will contain pointers
        to the output note audio, and the metadata relating to it.

    note_audio_dir : str
        Path to store the resulting audio file.

    pass_through : bool
        If True, don't bother trying to segment the audio.
    """
    logger.info("Begin segment_audio()")
    logger.debug("Loading segment index")
    segment_df = pd.read_csv(segment_index_file, index_col=0)
    logger.debug("loaded {} records.".format(
        len(segment_df)))

    # If we're passing through, keep all of them.
    if not pass_through:
        segment_df = segment_df[segment_df['onsets_file'].notnull()]
        logger.debug("Filtered {} records without onset files.".format(
            len(segment_df)))

        # Also, if passing through we don't need this.
        boltons.fileutils.mkdir_p(note_audio_dir)

    # pass_through and not pass_through are separated to keep
    # them as fast as possible.
    if pass_through:
        # This adds a zero to the index so it matches the format
        # of the multiindex.
        notes_df = segment_df.copy().set_index(
            [segment_df.index.tolist(), [0] * len(segment_df)])
        note_files = notes_df['audio_file']
        notes_df['note_file'] = note_files
    else:
        notes_index = pd.MultiIndex(levels=[[], []],
                                    labels=[[], []],
                                    names=['hash', 'note_idx'])
        notes_columns = segment_df.columns.tolist() + ['note_file']
        notes_df = pd.DataFrame(columns=notes_columns, index=notes_index)
        count = 0
        for idx, row in segment_df.iterrows():
            audio_file = row['audio_file']
            onset_file = row['onsets_file']
            note_files = segment_audio_from_onsets(
                audio_file, onset_file, note_audio_dir)
            logger.debug("Generated {} note files ({} of {}).".format(
                len(note_files), (count + 1), len(segment_df)))

            for i, x in enumerate(note_files):
                notes_df.loc[(idx, i), :] = row.tolist() + [x]
            if PRINT_PROGRESS:
                print("Progress: {:0.1f}% ({} of {})\r".format(
                    (((count + 1) / float(len(segment_df))) * 100.),
                    (count + 1), len(segment_df)), end='')
                sys.stdout.flush()
            count += 1

            if limit_n_files and count >= limit_n_files:
                break

        if PRINT_PROGRESS:
            print()

    notes_df.to_csv(note_index_file)
    logger.debug("Wrote note index to {} with {} records".format(
        note_index_file, len(notes_df)))
    logger.info("Completed segment_audio()")


if __name__ == "__main__":
    arguments = docopt(__doc__)

    level = 'INFO' if not arguments.get('--verbose') else 'DEBUG'
    logging.config.dictConfig(minst.logger.get_config(level))
    PRINT_PROGRESS = not arguments['--verbose']

    t0 = time.time()
    segment_audio(arguments['<segment_index>'],
                  arguments['<note_index>'],
                  arguments['<note_audio_dir>'],
                  arguments['--pass_thru'],
                  int(arguments['--limit']) if arguments['--limit'] else None)
    t_end = time.time()
    print("segment_audio completed in: {}s".format(t_end - t0))
