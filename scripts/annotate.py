#!/usr/bin/env python

"""
Show how to connect to keypress events
"""
from __future__ import print_function
import argparse
import claudio
import matplotlib
import numpy as np
import pandas as pd
import sys
import time

matplotlib.use("TkAGG")

import matplotlib.pyplot as plt
import minst.signal as S


class OnsetCanvas(object):

    def __init__(self, audio_file, output_file, onset_data=None,
                 nhop=100, group=None, target=None, title=None,
                 verbose=None):

        self.fig, self.axes = plt.subplots(nrows=2, ncols=1,
                                           figsize=(16, 6))

        x, fs = claudio.read(audio_file, samplerate=22050,
                             channels=1, bytedepth=2)

        onset_data = pd.DataFrame([]) if onset_data is None else onset_data
        self.output_file = output_file
        self.x_max = np.abs(x).max()
        self.trange = np.arange(0, len(x), nhop) / float(fs)
        self.waveform = x.flatten()[::nhop]
        self.envelope = S.log_envelope(x, fs, nhop)[::nhop]
        # self.onset_data = onset_data
        self.wave_handle = self.axes[0].plot(self.trange, self.waveform)
        self.env_handle = self.axes[1].plot(self.trange, self.envelope)
        self.onset_handles = []
        self.refresh_xlim()

        title = '' if not title else title
        title = "{}\nx: write and close / w: write / q: close"
        self.axes[0].set_title(title)

        self.set_onset_data(onset_data)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self._alive = False

    def run(self):
        self._alive = True
        while self.alive:
            time.sleep(0.1)

    @property
    def alive(self):
        return self._alive

    def set_onset_data(self, onset_data):
        self.onset_data = onset_data
        self.redraw_onset_data()
        plt.draw()

    def save_onsets(self):
        self.onset_data.to_csv(self.output_file)

    def redraw_onset_data(self):
        print("redrawing onsets")
        if not self.has_onsets:
            print("Doesn't have any: {}".format(self.onset_data))
            return

        for hnd in self.onset_handles:
            hnd.remove()

        self.onset_handles = []
        print("drawing lines : {}".format(self.onset_times))
        self.onset_handles += [self.axes[0].vlines(
            self.onset_data.time, ymin=-1.05*self.x_max,
            ymax=1.05*self.x_max, color='k', alpha=0.5, linewidth=3)]
        for t, i in zip(self.onset_data.time, self.onset_data.index):
            self.onset_handles += [self.axes[0].text(
                x=t, y=self.x_max, s=i, va='top', ha='left', fontsize=16)]

        self.onset_handles += [self.axes[1].vlines(
            self.onset_data.time, ymin=self.envelope.min()*1.05,
            ymax=0, color='k', alpha=0.5, linewidth=3)]
        for t, i in zip(self.onset_data.time, self.onset_data.index):
            self.onset_handles += [self.axes[1].text(
                x=t, y=-3, s=i, va='top', ha='left', fontsize=16)]

    def refresh_xlim(self):
        for ax in self.axes:
            ax.set_xlim(0, self.trange.max())
            ax.set_xlabel("Time (sec)")

    @property
    def has_onsets(self):
        return len(self.onset_data) > 0

    @property
    def onset_times(self):
        return np.asarray(self.onset_data.time)

    def on_key_press(self, event):
        """Handle key-press events.

        Catches the following:
            x : Write current onset data and close this canvas.
            w : Write current onset data.
            q : Close this canvas without saving.
            spacebar : Toggle a marker at the current mouse position.

        """
        print('Received: ', event.key)
        sys.stdout.flush()
        if event.key == 'x':
            print("Saving to: {}".format(self.output_file))
            self.save_onsets()
            plt.close()
            self._alive = False

        if event.key == 'w':
            print("Saving to: {}".format(self.output_file))
            self.save_onsets()

        elif event.key == 'q':
            print("Closing")
            plt.close()
            self._alive = False

        elif event.key == ' ':
            x, y = event.xdata, event.ydata
            print('({:4}, {:4})'.format(x, y))
            if self.has_onsets and (np.abs(self.onset_times - x) < 0.5).any():
                # Collision! Remove it
                idx = (np.abs(self.onset_data.time - x) < 0.5).nonzero()[0]
                print("Collision: {}".format(idx))
                od = self.onset_data.drop(
                    pd.Index([self.onset_data.index[idx[0]]]))
            else:
                print("New datapoint!")
                od = self.onset_data.append(dict(time=x), ignore_index=True)
            self.set_onset_data(od)


def annotate_one(audio_file, onset_file, output_file=None, title=None):
    if output_file is None:
        output_file = onset_file.replace(".csv", "-fix.csv")

    canvas = OnsetCanvas(audio_file, output_file, pd.read_csv(onset_file),
                         title=title)
    plt.show(block=True)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "index_file",
        metavar="index_file", type=str,
        help=".")
    parser.add_argument(
        "--verbose",
        metavar="verbose", type=int, default=0,
        help="Number of CPUs to use; by default, uses all.")

    args = parser.parse_args()
    dframe = pd.read_csv(args.index_file)

    for idx, row in dframe.iterrows():
        annotate_one(row.audio_file, row.onset_file, title=idx)
