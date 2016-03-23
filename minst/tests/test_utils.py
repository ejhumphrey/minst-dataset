import minst.utils


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
