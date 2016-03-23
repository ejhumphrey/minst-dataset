import minst.utils


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
