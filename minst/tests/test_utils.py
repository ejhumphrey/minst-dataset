import pytest
import glob
import os
import shutil
import tempfile

import minst.utils


DIRNAME = os.path.dirname(__file__)

@pytest.fixture()
def workspace(request):
    test_workspace = tempfile.mkdtemp()

    def fin():
        if os.path.exists(test_workspace):
            shutil.rmtree(test_workspace)

    request.addfinalizer(fin)

    return test_workspace


def collect_files(exts):
    afiles = []
    for n in range(7):
        fmt = os.path.join(DIRNAME, "/".join(["*"]*n), "*.{}*")
        for ext in exts:
            afiles += glob.glob(fmt.format(ext))

    return afiles


def __test(value, expected):
    assert value == expected


def test_generate_id():
    def __test_hash(prefix, result, hlen):
        assert result.startswith(prefix)
        assert len(result[len(prefix):]) == hlen

    tests = [("A", "foobar.mp3", 3),
             ("BC", "testwhat.foo", 8),
             ("TR", "i'matestfile.aiff", 12)]

    for prefix, name, hlen in tests:
        result = minst.utils.generate_id(prefix, name, hlen)
        yield __test_hash, prefix, result, hlen


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


def test_check_audio_file():
    for af in collect_files(['mp3', 'aif', 'aiff']):
        yield __test, minst.utils.check_audio_file(af), (True, None)

    for af in collect_files(['zip']):
        yield __test, minst.utils.check_audio_file(af)[0], False


def test_check_many_audio_files():
    afiles = collect_files(['mp3', 'aif', 'aiff'])
    for sterr in minst.utils.check_many_audio_files(afiles):
        yield __test, sterr, (True, None)

    other_files = collect_files(['zip'])
    for sterr in minst.utils.check_many_audio_files(other_files):
        yield __test, sterr[0], False


def test_trim(workspace):
    afiles = collect_files(['mp3', 'aif', 'aiff'])
    ofile = minst.utils.trim(afiles[0], workspace, 0.5)
    assert ofile

    other_files = collect_files(['zip'])
    ofile = minst.utils.trim(other_files[0], workspace, 0.5)
    assert ofile is None
