"""Download a collection of files from a list of HTTP URLs.

Example:
$ python src/utils/download.py data/uiowa.json ~/uiowa
"""

import argparse
from joblib import Parallel, delayed
import json
import logging
import os
import six.moves.urllib.error as urlerror
import six.moves.urllib.parse as urlparse
import six.moves.urllib.request as urlrequest
import sys
import time

logger = logging.getLogger()


def url_to_filepath(url, output_dir):
    """Create a valid output filepath for a given URL.

    Parameters
    ----------
    url : str
        File that will be downloaded.

    output_dir : str
        Base path to contain the output file.
    """
    output_file = os.path.join(output_dir, url.split('http://')[-1])
    outdir = os.path.dirname(output_file)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    return output_file


def download_one(url, output_file, skip_existing=True):
    """Download a single URL.

    Parameters
    ----------
    url : str
        URL to download.

    output_file : str
        Path to save the downloaded file.

    skip_existing : bool, default=True
        If True, down download URLs that exist in the output directory.

    Returns
    -------
    success : bool
        True if the file was downloaded successfully.
    """
    if os.path.exists(output_file) and skip_existing:
        print(" Skipping (exists): {}".format(url))
        return

    print("[{}] Fetching: {}".format(time.asctime(), url))
    try:
        surl = urlparse.quote(url, safe=':./')
        urlrequest.urlretrieve(surl, output_file)
    except urlerror.HTTPError:
        logger.warning("FAILED to download file at: {}".format(surl))
        logger.warning("\nOriginal link: {}\nOutput file:{}\n".format(
            url, output_file))
        logger.warning("Skipping...")
    finally:
        return os.path.exists(output_file)


def download_many(urls, output_files, skip_existing=True, num_cpus=-1):
    """Download a number of URLs.

    Parameters
    ----------
    urls : list of str, len=n
        Set of URLs to download.

    output_files : str, len=n
        Output files aligned to `urls`.

    skip_existing : bool, default=True
        If True, down download URLs that exist in the output directory.

    num_cpus : int, default=-1
        Number of CPUs to use for parallel downloads; -1 for all.

    Returns
    -------
    success : bool
        True if all URLs downloaded successfully.
    """
    if len(urls) != len(output_files):
        raise ValueError(
            "Number of URLs ({}) does not match the number of output files "
            "({})".format(len(urls), len(output_files)))

    pool = Parallel(n_jobs=num_cpus)
    fx = delayed(download_one)
    pairs = zip(urls, output_files)
    success = pool(fx(url, fout, skip_existing) for url, fout in pairs)
    return all(success)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest_file",
        metavar="manifest_file", type=str,
        help="A JSON file of URLs under 'resources'.")
    parser.add_argument(
        "output_dir",
        metavar="output_dir", type=str,
        help="Output path for downloaded data.")
    parser.add_argument(
        "--skip_existing", action="store_true",
        help="If True, don't download files that already exist.")
    parser.add_argument(
        "--num_cpus",
        metavar="num_cpus", type=int, default=-1,
        help="Number of CPUs to use; by default, uses all.")

    logging.basicConfig(level=logging.INFO)

    args = parser.parse_args()
    urls = json.load(open(args.manifest_file))['resources']
    output_files = [url_to_filepath(url, args.output_dir) for url in urls]
    success = download_many(urls, output_files,
                            skip_existing=args.skip_existing,
                            num_cpus=args.num_cpus)

    sys.exit(0 if success else 1)
