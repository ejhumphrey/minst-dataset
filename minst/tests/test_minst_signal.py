import pytest

import claudio.sox
import numpy as np
import os

import minst.signal

TOLERANCE = 0.0001


def test_signal_extract_clip_shorter(audio_file, tmpdir):
    """Expects a soundfile greater than 3.0 seconds in duration"""
    exp_duration = 1.0
    start_time = 1.0
    full_duration = float(claudio.sox.soxi(audio_file, 'D'))
    assert full_duration > start_time + exp_duration

    output_file = os.path.join(
        str(tmpdir), "test_signal_extract_clip_shorter_output.wav")
    assert minst.signal.extract_clip(audio_file, output_file, start_time,
                                     start_time + exp_duration, None)
    obs_duration = float(claudio.sox.soxi(output_file, 'D'))
    assert np.abs(obs_duration - exp_duration) < TOLERANCE


def test_signal_extract_clip_longer_sowhat(audio_file, tmpdir):
    """Expects a soundfile greater than 3.0 seconds in duration"""

    start_time = 1.0
    exp_duration = float(claudio.sox.soxi(audio_file, 'D')) - start_time
    assert exp_duration > 0.0

    output_file = os.path.join(
        str(tmpdir), "test_signal_extract_clip_longer_sowhat_output.wav")
    assert minst.signal.extract_clip(audio_file, output_file, start_time,
                                     start_time + 9.0, None)
    obs_duration = float(claudio.sox.soxi(output_file, 'D'))
    assert np.abs(obs_duration - exp_duration) < TOLERANCE


def test_signal_extract_clip_longer_pad(audio_file, tmpdir):
    """Expects a soundfile greater than 3.0 seconds in duration"""

    start_time = 1.0
    clip_duration = 1.0
    real_duration = float(claudio.sox.soxi(audio_file, 'D'))
    assert real_duration > (start_time + clip_duration)

    desired_duration = 9.0
    output_file = os.path.join(
        str(tmpdir), "test_signal_extract_clip_longer_noisepad_output.wav")
    assert minst.signal.extract_clip(
        audio_file, output_file, start_time,
        start_time + clip_duration, desired_duration)
    obs_duration = float(claudio.sox.soxi(output_file, 'D'))
    assert np.abs(obs_duration - desired_duration) < TOLERANCE
