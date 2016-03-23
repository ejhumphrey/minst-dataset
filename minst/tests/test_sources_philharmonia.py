import pytest
import os

import helpers
import minst.sources.philharmonia as philz


def test_parse_phil_path():
    test_pairs = [("banjo_B3_very-long_piano_normal.mp3",
                   ("banjo", "B3", "very-long", "piano", "normal")),
                  ("cello_A3_1_fortissimo_arco-normal.mp3",
                   ("cello", "A3", "1", "fortissimo", "arco-normal")),
                  ("trumpet_A3_15_pianissimo_normal.mp3",
                   ("trumpet", "A3", "15", "pianissimo", "normal")),
                  ("double-bass_A1_1_mezzo-forte_arco-normal",
                   ("double-bass", "A1", "1", "mezzo-forte", "arco-normal")),
                  ("/Users/cjacoby/data/philharmonia/www.philharmonia.co.uk/"
                   "assets/audio/samples/double bass/double bass"
                   "/double-bass_E1_phrase_mezzo-forte_arco-au-talon.mp3",
                   ("double-bass", "E1", "phrase", "mezzo-forte",
                    "arco-au-talon"))]

    for value, expected in test_pairs:
        result = philz.parse(value)
        yield helpers.__test, result, expected


def test_philz_collect():
    """Test that an input folder with files in rwc format is correctly
    converted to a dataframe."""
    philz_dir = os.path.join(os.path.dirname(__file__), 'dummy_philharmonia')

    philz_df = philz.collect(philz_dir)
    yield helpers.__test_df_has_data, philz_df
    yield helpers.__test_pd_output, philz_df, philz.NAME
