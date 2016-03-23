import os
import pytest
import shutil
import tempfile

import download as DL


@pytest.fixture()
def workspace(request):
    test_workspace = tempfile.mkdtemp()

    def fin():
        if os.path.exists(test_workspace):
            shutil.rmtree(test_workspace)

    request.addfinalizer(fin)

    return test_workspace


def test_download_one(workspace):
    url = ("https://www.wikipedia.org/portal/wikipedia.org/assets/img/"
           "Wikipedia_wordmark@2x.png")
    fout = os.path.join(workspace, "foo.png")
    assert DL.download_one(url, fout)


def test_download_many(workspace):
    urls = ["https://www.wikipedia.org/portal/wikipedia.org/assets/img/"
            "Wikipedia_wordmark@2x.png",
            "https://www.wikipedia.org/portal/wikipedia.org/assets/img/"
            "Wikipedia-logo-v2@2x.png"]
    output_files = [os.path.join(workspace, fname)
                    for fname in ('foo.png', 'bar.png')]
    assert DL.download_many(urls, output_files)
