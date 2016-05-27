# minst-dataset

The MNIST of music instrument sounds.

## Installing Dependencies

```
$ pip install -r requirements
$ pip install git+git://github.com/ejhumphrey/minst-dataset.git
```

## Building the dataset from scratch

### Get the data

This project uses three different solo instrument datasets.
- [University of Iowa - MIS](http://theremin.music.uiowa.edu/MIS.html)
- [Philharmonia](http://www.philharmonia.co.uk/explore/make_music)
- [RWC - Instruments](https://staff.aist.go.jp/m.goto/RWC-MDB/rwc-mdb-i.html)

We provide "manifest" files with which one can download the first two collections. For access to the third (RWC), you should contact the kind folks at AIST.

To download the data, you can invoke the following from your cloned repository:

```
$ python scripts/download.py data/uiowa.json ~/data/uiowa
...
$ python scripts/download.py data/philharmonia.json ~/data/philharmonia
```

### Segmenting the audio

Both the UIowa and RWC collections ship as recordings with multiple notes per file. To establish a clean dataset with which to work, it is advisable to split up these recordings (roughly) at note onsets.

Somewhat surprisingly, modern onset detection algorithms have not been optimized for this use case, and it is challenging to find a single parameterization that works well over the entire collection. To overcome this deficiency, we take a human-in-the-loop approach to robustly arrive at good cut-points for these (and future) collections.

First, collect a single dataset:

```
$ python scripts/collect_data.py uiowa path/to/download uiowa_index.csv
```

Optionally, you can run a segmentation algorithm over the resulting index. This will generate a number of best-guess onsets, saved out as CSV files under the same index as the collection, and an new dataframe tracking where these aligned files live locally (`uiowa_onsets/segment_index.csv` below):

```
$ python scripts/segment_collection.py uiowa_index.csv uiowa_onsets \
    segment_index.csv --method onsets --num_cpus -1 --verbose 50
```

Either way, you'll want to verify and correct (as needed) the estimated onsets. To do so, drop into the annotation routine by the following:

```
$ python scripts/annotate.py uiowa_onsets/segment_index.csv
```

In this GUI, `spacebar` will add / remove a marker at the location of the mouse cursor. The primary key commands are like `vi`: `w` will write the current markers; `q` will close without saving; `x` will write onset data and close. To kill the process entirely, interrupt the python program via terminal.

Improvements / enhancements are more than welcomed.

