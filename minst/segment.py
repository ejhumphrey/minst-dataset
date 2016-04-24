import claudio
import jams
import librosa
import numpy as np
import scipy.signal as sig

import minst.hll as H
import minst.utils as utils


def hll_split(filename, mfilt_len=51, threshold=0.5, delta=0.5, wait=100):
    time_points, freqs, amps = H.hll(filename)
    freqs = sig.medfilt(freqs, mfilt_len)
    amps = sig.medfilt(amps, mfilt_len)

    voicings = (freqs * amps) > threshold
    c_n = utils.canny(25, 3.5, 1)

    novelty = sig.lfilter(c_n, [1], voicings > .5)
    onsets = novelty * (novelty > 0)
    offsets = -novelty * (novelty < 0)
    onset_idx = librosa.onset.onset_detect(
        onset_envelope=onsets, delta=delta, wait=wait)
    offset_idx = librosa.onset.onset_detect(
        onset_envelope=offsets, delta=delta, wait=wait)

    onset_times = time_points[onset_idx]
    offset_times = time_points[offset_idx]
    return onset_times, offset_times


def logcqt_split(filename, pre_max=0, post_max=1, pre_avg=0,
                 post_avg=1, delta=0.05, wait=50):
    """
    Parameters
    ----------
    filename : str
        Path to an audiofile to split.

    Returns
    -------
    onsets : np.ndarray, ndim=1
        Times in seconds for splitting.
    """
    x, fs = claudio.read(filename, samplerate=22050,
                         channels=1, bytedepth=2)
    hop_length = 1024
    x_noise = x + np.random.normal(scale=10.**-3, size=x.shape)
    cqt = librosa.cqt(x_noise.flatten(),
                      sr=fs, hop_length=hop_length, fmin=27.5,
                      n_bins=24*8, bins_per_octave=24, tuning=0,
                      sparsity=0, real=False, norm=1)
    cqt = np.abs(cqt)
    lcqt = np.log1p(5000*cqt)

    c_n = utils.canny(51, 3.5, 1)
    onset_strength = sig.lfilter(c_n, np.ones(1), lcqt, axis=1).mean(axis=0)

    peak_idx = librosa.onset.onset_detect(
        onset_envelope=onset_strength, delta=delta, wait=wait)
    return librosa.frames_to_time(peak_idx, hop_length=hop_length)


def envelope_split(filename):
    """
    Parameters
    ----------
    filename : str
        Path to an audiofile to split.

    Returns
    -------
    onsets : np.ndarray, ndim=1
        Times in seconds for splitting.
    """
    x, fs = claudio.read(filename, samplerate=22050,
                         channels=1, bytedepth=2)

    log_env = 10*np.log10(10.**-4.5 + np.power(x.flatten()[:], 2.0))
    w_n = np.hanning(100)
    w_n /= w_n.sum()
    log_env_lpf = sig.filtfilt(w_n, np.ones(1), log_env)

    n_hop = 100
    kernel = utils.canny(100, 3.5, 1)
    kernel /= np.abs(kernel).sum()
    onsets_forward = sig.lfilter(
        kernel, np.ones(1),
        log_env_lpf[::n_hop] - log_env_lpf.min(), axis=0)

    onsets_pos = onsets_forward * (onsets_forward > 0)
    peak_idx = librosa.util.peak_pick(onsets_pos,
                                      pre_max=500, post_max=500, pre_avg=10,
                                      post_avg=10, delta=0.025, wait=100)
    return librosa.frames_to_time(peak_idx, hop_length=n_hop)
