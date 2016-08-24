import pytest

import glob
import logging.config
import os

import minst.logger
import minst.utils

logging.config.dictConfig(minst.logger.get_config('INFO'))


def collect_files(exts, data, depth=8):
    afiles = []
    for n in range(depth):
        fmt = os.path.join(data, "/".join(["*"] * n), "*.{}*")
        for ext in exts:
            afiles += glob.glob(fmt.format(ext))

    return afiles


def __test(value, expected):
    assert value == expected


def test_generate_id():
    def __test_hash(prefix, result, hlen, exp):
        assert result.startswith(prefix)
        assert len(result[len(prefix):]) == hlen
        assert result == exp

    tests = [("A", "foobar.mp3", 3, 'A6fb'),
             ("BC", "testwhat.foo", 8, 'BC87188425'),
             ("TR", "i'matestfile.aiff", 12, 'TR35a75e8d3dcb')]

    for prefix, name, hlen, exp in tests:
        result = minst.utils.generate_id(prefix, name, hlen)
        yield __test_hash, prefix, result, hlen, exp


def test_get_note_distance():
    test_pairs = [(('Bb1', 'B1'), 1),
                  (('C4', 'B4'), 11),
                  (('Bb1', 'B2'), 13),
                  (('C3', 'C4'), 12),
                  (('F5', 'F5'), 0),
                  (('C#3', 'C4'), 11)]

    for value, expected in test_pairs:
        result = minst.utils.note_distance(value)
        yield __test, result, expected


def test_check_audio_file(data_root):
    for af in collect_files(['mp3', 'aif', 'aiff'], data_root):
        __test(minst.utils.check_audio_file(af), (True, None))

    for af in collect_files(['zip'], data_root):
        __test(minst.utils.check_audio_file(af)[0], False)

    __test(minst.utils.check_audio_file('heavy_metal.wav')[0], False)


def test_check_many_audio_files(data_root):
    afiles = collect_files(['mp3', 'aif', 'aiff'], data_root)
    for sterr in minst.utils.check_many_audio_files(afiles):
        __test(sterr, (True, None))

    other_files = collect_files(['zip'], data_root)
    for sterr in minst.utils.check_many_audio_files(other_files):
        __test(sterr[0], False)


def test_trim(workspace, data_root):
    afiles = collect_files(['mp3', 'aif', 'aiff'], data_root)
    ofile = minst.utils.trim(afiles[0], workspace, 0.5)
    assert ofile

    other_files = collect_files(['zip'], data_root)
    ofile = minst.utils.trim(other_files[0], workspace, 0.5)
    assert ofile is None
