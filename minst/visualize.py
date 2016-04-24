import claudio
import matplotlib.pyplot as plt
import numpy as np

import minst.signal as S


def draw_onset_data(audio_file, onset_data, title):
    x, fs = claudio.read(audio_file, samplerate=22050, channels=1, bytedepth=2)
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 6))
    nhop = 100
    x_max = np.abs(x).max()
    trange = np.arange(0, len(x), nhop) / float(fs)

    axes[0].plot(trange, x.flatten()[::nhop])
    if not onset_data.empty:
        axes[0].vlines(onset_data.time, ymin=-1.05*x_max, ymax=1.05*x_max,
                       color='k', alpha=0.5, linewidth=3)

    log_env_lpf = S.log_envelope(x, fs, 100)
    axes[1].plot(trange, log_env_lpf[::nhop])
    if not onset_data.empty:
        axes[1].vlines(onset_data.time, ymin=log_env_lpf.min()*1.05,
                       ymax=0, color='k', alpha=0.5, linewidth=3)

    for ax in axes:
        ax.set_xlim(0, trange.max())
        ax.set_xlabel("Time (sec)")

    axes[0].set_title(title)

    return fig
