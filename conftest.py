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
def uiowa_root(data_root):
    return os.path.join(data_root, RAW, 'dummy_uiowa')


@pytest.fixture()
def philz_root(data_root):
    return os.path.join(data_root, RAW, 'dummy_philharmonia')


@pytest.fixture()
def rwc_root(data_root):
    return os.path.join(data_root, RAW, 'dummy_rwc')


@pytest.fixture()
def workspace(request):
    test_workspace = tempfile.mkdtemp()

    def fin():
        if os.path.exists(test_workspace):
            shutil.rmtree(test_workspace)

    request.addfinalizer(fin)

    return test_workspace
