import pytest
import shutil
import tempfile

import os

DATA = 'data'
RAW = 'raw_dataroot'


@pytest.fixture()
def data_root():
    return os.path.join(os.path.dirname(__file__), DATA)


@pytest.fixture()
def onset_root(data_root):
    return os.path.join(data_root, 'onsets')


@pytest.fixture()
def raw_data_root(data_root):
    return os.path.join(data_root, RAW)


@pytest.fixture()
def uiowa_root(raw_data_root):
    return os.path.join(raw_data_root, 'dummy_uiowa')


@pytest.fixture()
def philz_root(raw_data_root):
    return os.path.join(raw_data_root, 'dummy_philharmonia')


@pytest.fixture()
def rwc_root(raw_data_root):
    return os.path.join(raw_data_root, 'dummy_rwc')


@pytest.fixture()
def goodsounds_root(raw_data_root):
    return os.path.join(raw_data_root, 'dummy_goodsounds')


@pytest.fixture()
def audio_file(goodsounds_root):
    return os.path.join(goodsounds_root, 'sound_files', 'bass',
                        'bass_alejandro_recordings', 'neumann', '0005.wav')


@pytest.fixture()
def workspace(request):
    test_workspace = tempfile.mkdtemp()

    def fin():
        if os.path.exists(test_workspace):
            shutil.rmtree(test_workspace)

    request.addfinalizer(fin)

    return test_workspace
