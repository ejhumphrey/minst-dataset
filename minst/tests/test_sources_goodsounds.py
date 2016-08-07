import helpers
import minst.sources.goodsounds as goodsounds


def test_parse_goodsounds_path():
    test_pairs = [
        # including sound_files dir.
        ("sound_files/alto sax/sax_alto_scale_2_raul_recordings/"
         "neumann/0005.wav",
         ("alto sax", "sax_alto_scale_2_raul_recordings", "neumann",
          "0005")),
        # a complete, full path
        ('/Users/username/data/good-sounds/sound_files/oboe/'
         'oboe_marta_recordings/iphone/0249.wav',
         ('oboe', 'oboe_marta_recordings', 'iphone', '0249')),
        ('trumpet/trumpet_jesus_improvement_recordings/neumann/1234.wav',
         ('trumpet', 'trumpet_jesus_improvement_recordings', 'neumann',
          '1234'))]

    for value, expected in test_pairs:
        result = goodsounds.parse(value)
        yield helpers.__test, result, expected


def test_goodsounds_df_collect(goodsounds_root):
    """Test that an input folder with files in rwc format is correctly
    converted to a dataframe."""
    goodsounds_df = goodsounds.collect(goodsounds_root)
    helpers.__test_df_has_data(goodsounds_df)
    helpers.__test_pd_output(goodsounds_df, goodsounds.NAME)
