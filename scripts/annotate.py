#!/usr/bin/env python

"""
A GUI tool for annotating onsets in audio files.

Example of how to run:
 > python scripts/annotate.py onsets/rwc/segment_index.csv --verbose

 See the README.md for more detailed information.

Keys:

"""
from __future__ import print_function
import argparse
import claudio
import logging
import matplotlib
import numpy as np
import os
import pandas as pd
import pprint
import sys
import time

matplotlib.use("TkAGG")

import matplotlib.pyplot as plt
import minst.logger
import minst.signal as S

logger = logging.getLogger(__name__)


class OnsetCanvas(object):

    def __init__(self, audio_file, output_file, onset_data=None,
                 nhop=100, group=None, target=None, title=None,
                 verbose=None):

        self.fig, self.axes = plt.subplots(nrows=3, ncols=1,
                                           figsize=(20, 6))

        self.x, self.fs = claudio.read(audio_file, samplerate=22050,
                                       channels=1, bytedepth=2)

        onset_data = pd.DataFrame([]) if onset_data is None else onset_data
        self.output_file = output_file
        self.x_max = np.abs(self.x).max()
        self.trange = np.arange(0, len(self.x), nhop) / float(self.fs)
        self.waveform = self.x.flatten()[::nhop]
        self.envelope = S.log_envelope(self.x, self.fs, nhop)[::nhop]
        self.lcqt = S.logcqt(self.x, self.fs)

        # self.onset_data = set_onset_data
        self.wave_handle = self.axes[0].plot(self.trange, self.waveform)
        self.env_handle = self.axes[1].plot(self.trange, self.envelope)
        self.lcqt_handle = self.axes[2].imshow(self.lcqt,
            aspect='auto', origin='lower', interpolation='nearest')
        self.onset_handles = []
        self.refresh_xlim()

        title = '' if not title else title
        title = ("{}\nx: write and close / w: write / q: close / c: clear / "
                 "SPACE: set/delete marker\n"
                 "1: envelope onsets / 2: logcqt onsets".format(title))
        self.axes[0].set_title(title)

        self.set_onset_data(onset_data)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self._alive = False
        self._quit = False
        self._mark_for_later = False

    def run(self):
        self._alive = True
        while self.alive:
            time.sleep(0.1)

    @property
    def quit(self):
        return self._quit

    @property
    def alive(self):
        return self._alive

    def set_onset_data(self, onset_data):
        self.onset_data = onset_data
        self.redraw_onset_data()
        plt.draw()

    def save_onsets(self):
        self.onset_data.to_csv(self.output_file)

    def clear_onsets(self):
        self.onset_data = pd.DataFrame([])
        for hnd in self.onset_handles:
            hnd.remove()
        self.onset_handles = []
        plt.draw()

    def redraw_onset_data(self):
        logger.debug("redrawing onsets")
        if not self.has_onsets:
            logger.debug("Doesn't have any: {}".format(self.onset_data))
            return

        logger.debug("\nOnsets to draw: {}\nHandles: {}".format(
            self.onset_data, self.onset_handles))

        for hnd in self.onset_handles:
            hnd.remove()

        logger.debug("Plotting the following onsets: {}".format(
            self.onset_data))

        self.onset_handles = []
        logger.debug("drawing lines : {}".format(self.onset_times))
        self.onset_handles += [self.axes[0].vlines(
            self.onset_data.time, ymin=-1.05 * self.x_max,
            ymax=1.05 * self.x_max, color='k', alpha=0.5, linewidth=3)]
        for t, i in zip(self.onset_data.time, self.onset_data.index):
            self.onset_handles += [self.axes[0].text(
                x=t, y=self.x_max, s=i, va='top', ha='left', fontsize=16)]

        self.onset_handles += [self.axes[1].vlines(
            self.onset_data.time, ymin=self.envelope.min() * 1.05,
            ymax=0, color='k', alpha=0.5, linewidth=3)]
        for t, i in zip(self.onset_data.time, self.onset_data.index):
            self.onset_handles += [self.axes[1].text(
                x=t, y=-3, s=i, va='top', ha='left', fontsize=16)]

    def refresh_xlim(self):
        for ax in self.axes[:-1]:
            ax.set_xlim(0, self.trange.max())
            ax.set_xlabel("Time (sec)")

    @property
    def has_onsets(self):
        return len(self.onset_data) > 0

    @property
    def onset_times(self):
        return np.asarray(self.onset_data.time)

    def shift_onsets(self, amount):
        if self.has_onsets:
            new_onsets = self.onset_data.copy() + amount
            self.set_onset_data(new_onsets)

    def modify_onsets_at_time(self, x, threshold=0.5, create=True):
        """Delete any offsets that occur at time +/- a threshold.

        Returns True if any are deleted, False otherwise.

        Parameters
        ----------
        x : float
            Time in seconds

        threshold : float
            In seconds.
        """
        od = None
        # Debugging checks
        if self.has_onsets:
            if self.onset_times is None:
                logger.error("Onset Times is None!")
        if x is None:
            logger.error("modify_onsets_at_time() - x is None!")
        if threshold is None:
            logger.error("modify_onsets_at_time() - Threshold is None!")

        if (self.has_onsets and
                (np.abs(self.onset_times - x) < threshold).any()):
            # Collision! Remove it
            idx = (np.abs(self.onset_times - x) < threshold).nonzero()[0]
            logger.debug("Collision: {}".format(idx))
            od = self.onset_data.drop(
                pd.Index([self.onset_data.index[idx[0]]]))
        # If there's no onset at this location and create mode is on.
        elif create:
            logger.debug("New datapoint!")
            od = self.onset_data.append(dict(time=x), ignore_index=True)
        if od is not None:
            self.set_onset_data(od)

    def on_key_press(self, event):
        """Handle key-press events.

        Catches the following:
            x : Write current onset data and close this canvas.
            w : Write current onset data.
            q : Close this canvas without saving.
            spacebar : Toggle a marker at the current mouse position.
            c : Clear all current onsets
        """
        logger.debug('Received: {}'.format(event.key))
        sys.stdout.flush()
        if event.key == 'Q':
            logger.info("Quitting")
            plt.close()
            self._alive = False
            self._quit = True

        elif event.key == 'x':
            logger.info("Saving to: {}".format(self.output_file))
            self.save_onsets()
            plt.close()
            self._alive = False

        elif event.key == 'w':
            logger.info("Saving to: {}".format(self.output_file))
            self.save_onsets()

        elif event.key == 'q':
            logger.info("Closing")
            plt.close()
            self._alive = False

        elif event.key == 'c':
            logger.info("Clearing existing markers")
            self.clear_onsets()

        elif event.key == 'm':
            logger.info("Marking for later")
            self._mark_for_later = True
            plt.close()
            self._alive = False

        elif event.key == ' ':
            x, y = event.xdata, event.ydata
            logger.debug('({:4}, {:4})'.format(x, y))
            self.modify_onsets_at_time(x)

        elif event.key == 'd':
            # Delete in a larger range (1s)
            x, y = event.xdata, event.ydata
            logger.info('({:4}, {:4})'.format(x, y))
            self.modify_onsets_at_time(x, threshold=1.0, create=False)

        elif event.key == 'D':
            # Delete in an even larger range (5s)
            x, y = event.xdata, event.ydata
            logger.info('({:4}, {:4})'.format(x, y))
            self.modify_onsets_at_time(x, threshold=5.0, create=False)

        # Use onset detectors to get started
        elif event.key == '1':
            logger.debug("Getting envelope_onsets(.008)")
            onsets = S.envelope_onsets(self.x, self.fs,
                                       wait=int(self.fs * .008))
            self.set_onset_data(pd.DataFrame(dict(time=onsets)))

        elif event.key == '2':
            # Reset onsets with "envelope_onsets"
            logger.debug("Getting envelope_onsets(.01)")
            onsets = S.envelope_onsets(self.x, self.fs,
                                       wait=int(self.fs * .01))
            self.set_onset_data(pd.DataFrame(dict(time=onsets)))

        elif event.key == '3':
            # Reset onsets with "envelope_onsets"
            logger.debug("Getting envelope_onsets(.02)")
            onsets = S.envelope_onsets(self.x, self.fs,
                                       wait=int(self.fs * .02))
            self.set_onset_data(pd.DataFrame(dict(time=onsets)))

        elif event.key == '4':
            # Reset onsets with "envelope_onsets"
            logger.debug("Getting envelope_onsets(.05)")
            onsets = S.envelope_onsets(self.x, self.fs,
                                       wait=int(self.fs * .05))
            self.set_onset_data(pd.DataFrame(dict(time=onsets)))

        elif event.key == '5':
            pass

        elif event.key == '6':
            # Reset onsets with "logcqt_onsets"
            logger.debug("Getting logcqt_onsets()")
            onsets = S.logcqt_onsets(self.x, self.fs,
                                     wait=int(self.fs * .01))
            self.set_onset_data(pd.DataFrame(dict(time=onsets)))

        elif event.key == '7':
            # Reset onsets with "logcqt_onsets"
            logger.debug("Getting logcqt_onsets()")
            onsets = S.logcqt_onsets(self.x, self.fs,
                                     wait=int(self.fs * .02))
            self.set_onset_data(pd.DataFrame(dict(time=onsets)))

        elif event.key == 'left':
            # Shift all markers to the left (subtract) by 10ms/.01s
            self.shift_onsets(-.01)

        elif event.key == 'right':
            # Shift all markers to the left (subtract) by 10ms/.01s
            self.shift_onsets(.01)

        elif event.key == 'up':
            # Shift all markers to the left (subtract) by 100ms/.1s
            self.shift_onsets(-.1)

        elif event.key == 'down':
            # Shift all markers to the left (subtract) by 100ms/.1s
            self.shift_onsets(.1)


def annotate_one(audio_file, onset_file, output_file=None, title=None,
                 skip_existing=False):
    if output_file is None:
        output_file = onset_file.replace(".csv", "-fix.csv")

    if os.path.exists(output_file):
        if skip_existing:
            return False, False
        onset_file = output_file

    logger.info("Working on audio: {}".format(audio_file))
    logger.info("Onset_file: {}".format(onset_file))
    logger.info("Title: {}".format(title))
    t0 = time.time()

    onsets = pd.read_csv(onset_file) if onset_file else pd.DataFrame([])
    canvas = OnsetCanvas(audio_file, output_file, onsets,
                         title=title)
    logger.info("Writing to: {}".format(output_file))
    plt.show(block=True)

    # Should we continue?
    t_end = time.time() - t0
    logger.info("Took {}s to work on {}".format(t_end, audio_file))
    return canvas.quit, canvas._mark_for_later


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "index_file",
        metavar="index_file", type=str,
        help=".")
    parser.add_argument(
        "--verbose", action='store_true', help="Set verbosity")
    parser.add_argument(
        '--startat', default=-1, type=int)
    parser.add_argument(
        '--marked_file', default='marked_for_later_idx.txt')
    parser.add_argument(
        '--skip_existing', action='store_true',
        help='If this file has already been edited, skip it.')
    parser.add_argument(
        '--ignore_no_instrument',
        action='store_true',
        help="Don't look at files that don't have an assciated instrument "
             "in the index_file")
    parser.add_argument(
        '--random',
        action='store_true',
        help="Choose a random file.")

    args = parser.parse_args()
    level = 'INFO' if not args.verbose else 'DEBUG'
    logging.config.dictConfig(minst.logger.get_config(level))

    dframe = pd.read_csv(args.index_file, index_col=0)
    if args.ignore_no_instrument:
        dframe = dframe.loc[dframe['instrument'].dropna().index]

    if not args.random:
        marked_idxs = []
        completed_idxs = []

        count = 0
        for n, (idx, row) in enumerate(dframe.iterrows()):
            if int(args.startat) >= 0 and n < args.startat:
                logger.info("Skipping {}".format(idx))
                continue

            logger.info("Annotating:\n{} [idx={}]".format(row, idx))
            # TODO(cbj): There should be a better way to handle this
            #  ... and/or a better naming scheme for the columns
            onsets_file = row.get('onsets_file', '')
            quit, marked = annotate_one(row.audio_file, onsets_file,
                                        skip_existing=args.skip_existing,
                                        title="{} of {} | instrument: {}"
                                        .format(count, len(dframe),
                                                row['instrument']))

            if quit:
                logger.info("Application Exiting...")
                break
            if marked:
                marked_idxs.append(idx)
            else:
                completed_idxs.append(idx)
            count += 1

        print("The following indexes were marked to return to:")
        pprint.pprint(marked_idxs)

        with open(args.marked_file, 'a') as fh:
            for index in marked_idxs:
                fh.write("{}\n".format(index))

        print("In this session, you completed {} files".format(
            len(completed_idxs)))
        print("In this session, you marked {} files".format(
            len(marked_idxs)))

    else:
        while True:
            row = dframe.sample()

            logger.info("Annotating:\n{}".format(row))
            # TODO(cbj): There should be a better way to handle this
            #  ... and/or a better naming scheme for the columns
            onsets = row.get('onset_file', row.get('logcqt', None))
            quit, marked = annotate_one(row.audio_file.iloc[0], onsets.iloc[0],
                                        skip_existing=False,
                                        title="{}| instrument: {}"
                                        .format(row.index[0], row['instrument'].iloc[0]))
            if quit:
                logger.info("Application Exiting...")
                break
