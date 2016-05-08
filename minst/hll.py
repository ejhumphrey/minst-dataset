import claudio.sox
import claudio.util
import numpy as np
import os
import pandas as pd
import subprocess

BIN = os.path.expanduser('~/hll/hll_mono')
PARAMS = os.path.expanduser('~/hll/HLL_MONO_PARAMS.csv')


def hll(filename):
    """Perform HLL-tracking over an audio file.

    Parameters
    ----------
    filename : str
        Audio file to process.

    Returns
    -------
    time_points, frequencies, amplitudes : np.ndarray, len=n
        Time, frequency, and amplitude vectors of the analysis.
    """
    deps = (BIN, PARAMS)
    if not all([os.path.exists(x) for x in deps]):
        raise EnvironmentError(
            "Requires the following files: {}".format(deps))
    samplerate = 44100.0
    tempfile = claudio.util.temp_file('.wav')
    output_file = claudio.util.temp_file('.csv')
    claudio.sox.convert(filename, tempfile,
                        samplerate=samplerate, channels=1,
                        bytedepth=2)
    if os.path.exists(output_file):
        os.remove(output_file)
    args = [BIN, tempfile, output_file, PARAMS]
    subprocess.check_output(args)

    (time_points, freqs,
        amps) = np.asarray(pd.read_csv(output_file, header=0)).T
    time_points = time_points / samplerate
    null_idx = amps > 0.999
    freqs[null_idx] = 0
    amps[null_idx] = 0
    return time_points, np.abs(freqs), np.abs(amps)
